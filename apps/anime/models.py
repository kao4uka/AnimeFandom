from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from apps.anime import constants
from apps.anime.utils import validate_image_size
from apps.anime.utils import upload_to_episode, upload_to_image


class Genre(models.Model):
    title = models.CharField(max_length=155, verbose_name='Название жанра')
    url = models.SlugField(max_length=100, blank=True, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Tag(models.Model):
    title = models.CharField(max_length=155, verbose_name='Название тега')
    url = models.SlugField(max_length=155)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Season(models.Model):
    name = models.CharField(max_length=100, verbose_name='Сезон')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Сезон'
        verbose_name_plural = 'Сезоны'


class Anime(models.Model):
    translated_title = models.CharField(max_length=255, verbose_name='Название')
    image = models.ImageField(upload_to=upload_to_image, validators=[validate_image_size], verbose_name='Превью фото')
    age_limit = models.IntegerField(choices=constants.AGE_LIMIT, verbose_name='Возрастной рейтинг')
    release_date = models.DateField(verbose_name='Год выпуска', )
    original_title = models.CharField(max_length=255, verbose_name='Оригинальное название')
    description = models.TextField(max_length=1555, verbose_name='Описание')
    genre = models.ManyToManyField(Genre, verbose_name='Жанры')
    status = models.CharField(
        max_length=2,
        choices=constants.Status.choices,
        default=constants.Status.NO_PUBLISH,
        verbose_name='Статус аниме'
    )
    tag = models.ManyToManyField(Tag, verbose_name='Теги')
    author = models.CharField(max_length=55, verbose_name='Автор')
    rating = models.PositiveIntegerField(choices=constants.RATING, default=1, verbose_name='Рейтинг')
    url = models.SlugField(max_length=100, blank=True, unique=True)
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return self.translated_title

    class Meta:
        verbose_name = 'Аниме'
        verbose_name_plural = 'Аниме'


class Episode(models.Model):
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, verbose_name='Аниме', related_name='episodes')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name='Сезон')
    episode_number = models.PositiveIntegerField(verbose_name='Серия')
    episode_title = models.CharField(max_length=35, verbose_name='Название серии')
    mp4 = models.FileField(upload_to=upload_to_episode, verbose_name='Видео')

    def __str__(self):
        return self.episode_title

    class Meta:
        verbose_name = 'Серия'
        verbose_name_plural = 'Серии'
        unique_together = (('anime', 'season', 'episode_number'),)




