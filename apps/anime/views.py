from django_filters import rest_framework as filters
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import generics, views, status, viewsets


from apps.anime.services import (
    get_anime_with_status,
    get_status_anime,
    get_favorite_anime,
    is_anime_in_favorites,
    add_anime_to_favorites,
    get_ordered_anime_queryset,
    remove_anime_from_favorites,
    change_anime_status_to_published
)
from apps.anime import constants
from apps.anime.serializers import *
from apps.anime.models import Anime, Episode
from apps.anime.filters import ORDERING_FIELDS
from apps.users.exceptions import AlreadyInFavoritesError


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 10000


class FavoriteListAPIView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user
        anime, favorite_anime_ids = get_favorite_anime(user)

        paginator = PageNumberPagination()
        paginator.page_size = 10

        page = paginator.paginate_queryset(anime, request)

        serialized_anime = AnimeSerializer(page, many=True)
        data = serialized_anime.data

        for anime_data in data:
            anime_id = anime_data.get('id')
            anime_data['selected'] = anime_id in favorite_anime_ids
        return paginator.get_paginated_response(data)


class AddToFavoritesAPIView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, anime_id, format=None):
        user = request.user
        try:
            anime = add_anime_to_favorites(user, anime_id)
            return Response({'message': 'Аниме добавлено в избранное'}, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({'message': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except AlreadyInFavoritesError:
            return Response({'message': 'Аниме уже в избранном'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'Невозможно добавить аниме в избранное'}, status=status.HTTP_400_BAD_REQUEST)


class RemoveFromFavoritesAPIView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, anime_id, format=None):
        user = request.user
        remove_anime_from_favorites(user, anime_id)
        return Response({'message': 'Аниме удалено из избранного'}, status=status.HTTP_200_OK)


class AnimeStatusAPIView(viewsets.ModelViewSet):
    queryset = get_anime_with_status(constants.Status.NO_PUBLISH)
    serializer_class = AnimeSerializer
    permission_classes = (permissions.IsAdminUser,)
    lookup_field = 'id'
    filter_backends = [SearchFilter]
    search_fields = ('id', 'translated_title', 'original_title', 'release_date')


class AnimeStatusDetailAPIView(generics.RetrieveAPIView):
    queryset = get_anime_with_status(constants.Status.NO_PUBLISH)
    serializer_class = AnimeSerializer
    permission_classes = (permissions.IsAdminUser,)
    lookup_field = 'id'

    def post(self, request, *args, **kwargs):
        anime = self.get_object()
        if anime.status == constants.Status.NO_PUBLISH:
            change_anime_status_to_published(anime)
            return Response({'message': 'Статус аниме изменен на "Опубликовано"'}, status=status.HTTP_200_OK)
        return Response({'message': 'Невозможно изменить статус аниме'}, status=status.HTTP_400_BAD_REQUEST)


class AnimeDetailAPIView(views.APIView):

    def get(self, request, *args, **kwargs):
        anime_id = kwargs.get('anime_id')

        anime = Anime.objects.get(id=anime_id)
        episodes = Episode.objects.filter(anime=anime).select_related('season').defer('mp4')

        anime_serializer = AnimeSerializer(anime)
        episode_serializer = EpisodeSerializer(episodes, many=True)

        return Response({
            'anime': anime_serializer.data,
            'episodes': episode_serializer.data
        })


class AnimeListAPIView(generics.ListAPIView):
    serializer_class = AnimeListSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_fields = (
        'translated_title',
        'genre',
        'tag',
        'original_title',
        'author',
        'age_limit',
        'release_date'
    )
    ordering_fields = ORDERING_FIELDS
    ordering = 'rating'

    def get_queryset(self):
        if get_status_anime():
            return get_ordered_anime_queryset(self.ordering)


class AnimeEpisodeDetailAPIView(views.APIView):
    def get(self, request, url, episode_number):
        anime = Anime.objects.only('translated_title', 'image', 'age_limit',).get(url=url)
        anime.episode = anime.episodes.get(episode_number=episode_number)
        serializer = AnimeEpisodeDetailSerializer(anime)
        return Response(serializer.data)

