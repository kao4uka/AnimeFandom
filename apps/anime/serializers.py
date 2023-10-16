from rest_framework import serializers
from apps.anime.models import Genre, Anime, Tag, Episode


# class SeasonSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Season
#         fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'title', 'url')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'title')


class AnimeSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    tag = TagSerializer(many=True)

    class Meta:
        model = Anime
        fields = (
            'id',
            'genre',
            'tag',
            'translated_title',
            'image',
            'age_limit',
            'release_date',
            'original_title',
            'description',
            'author'
        )


class EpisodeSerializer(serializers.ModelSerializer):
    season_name = serializers.CharField(source='season.name')

    class Meta:
        model = Episode
        fields = ('id', 'season_name', 'anime_id', 'episode_number', 'episode_title')


class AnimeListSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    tag = TagSerializer(many=True)
    total_episodes = serializers.IntegerField(read_only=True)
    total_seasons = serializers.IntegerField(read_only=True)

    class Meta:
        model = Anime
        fields = (
            'translated_title',
            'image',
            'original_title',
            'description',
            'genre',
            'tag',
            'author',
            'rating',
            'total_episodes',
            'total_seasons'
        )

    # def get_total_seasons(self, obj):
    #     return Episode.objects.filter(anime=obj).distinct('season').count()
    #
    # def get_total_episodes(self, obj):
    #     return Episode.objects.filter(anime=obj).count()


class EpisodeDetailSerializer(serializers.ModelSerializer):
    season_name = serializers.CharField(source='season.name')
    anime_title = serializers.CharField(source='anime.translated_title')

    class Meta:
        model = Episode
        exclude = ('season', 'anime')


class AnimeEpisodeDetailSerializer(serializers.ModelSerializer):
    episode = EpisodeDetailSerializer(read_only=True)

    class Meta:
        model = Anime
        fields = (
            'translated_title',
            'image',
            'age_limit',
            'episode'
        )
