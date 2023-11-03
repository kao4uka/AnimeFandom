from django.core.cache import cache
from django.db.models import Count
from django.views.decorators.cache import cache_page

from config.settings.base import CACHE_TIMEOUT
from apps.anime.filters import ORDERING_MAP
from apps.anime.models import Anime
from apps.anime import constants
from apps.users.exceptions import AlreadyInFavoritesError, AnimeNotFoundError
from apps.users.models import UserFavoriteAnime


def get_favorite_anime(user):

    
    cache_key = f'favorite_anime_{user.id}'
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    favorites_anime = UserFavoriteAnime.objects.filter(
        user=user,
        anime__status=constants.Status.PUBLISHED
    )

    anime_ids = [favorite.anime_id for favorite in favorites_anime]
    anime = Anime.objects.filter(pk__in=anime_ids).prefetch_related('genre', 'tag')

    cache.set(cache_key, (anime, set(anime_ids)), CACHE_TIMEOUT)
    return anime, set(anime_ids)


def remove_anime_from_favorites(user, anime_id):
    UserFavoriteAnime.objects.filter(user=user, anime_id=anime_id).delete()


def is_anime_in_favorites(user, anime_id):
    try:
        favorite_anime = UserFavoriteAnime.objects.get(user=user, anime_id=anime_id)
        return True
    except UserFavoriteAnime.DoesNotExist:
        return False


def add_anime_to_favorites(user, anime_id):
    try:
        anime = Anime.objects.get(id=anime_id, status=constants.Status.PUBLISHED)
        if not UserFavoriteAnime.objects.filter(user=user, anime_id=anime_id).exists():
            UserFavoriteAnime.objects.create(user=user, anime=anime)
            return anime
        else:
            raise AlreadyInFavoritesError()
    except Anime.DoesNotExist:
        raise AnimeNotFoundError()


def get_anime_with_status(status):
    return Anime.objects.filter(status=status).prefetch_related('genre', 'tag')


def change_anime_status_to_published(anime):
    anime.status = constants.Status.PUBLISHED
    anime.save()


def get_main_anime():
    return Anime.objects.order_by('rating')


def get_status_anime():
    cached_result = cache.get('status_anime_cached_key')
    if cached_result is not None:
        return cached_result
    else:
        result = Anime.objects.filter(status=constants.Status.PUBLISHED).only('status')

        cache.set('status_anime_cached_key', result, CACHE_TIMEOUT)
        return result


def get_users_image(request):
    image = request.user.image
    data = {'image': image}

    return data


def get_ordered_anime_queryset(ordering_param=None):
    cache_key = f'ordered_anime_queryset{ordering_param}'
    cached_ids = cache.get(cache_key)

    queryset = Anime.objects.annotate(
        total_episodes=Count('episodes'),
        total_seasons=Count('episodes__season', distinct=True)
    )

    if ordering_param and ordering_param in ORDERING_MAP:
        queryset = queryset.order_by(ORDERING_MAP[ordering_param])

    if not cached_ids:
        cached_ids = list(queryset.values_list('id', flat=True))
        cache.set(cache_key, cached_ids, CACHE_TIMEOUT)

    return Anime.objects.filter(id__in=cached_ids).prefetch_related('genre', 'tag')
