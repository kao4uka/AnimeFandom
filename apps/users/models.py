from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.dispatch import receiver
from django.db import models

from apps.anime.models import Anime
from apps.users.utils import validate_avatar_size
from apps.users.managers import UserManager
from apps.anime import constants


class User(AbstractBaseUser, PermissionsMixin):
    firstname = models.CharField(max_length=100, verbose_name='Имя')
    lastname = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(max_length=100, unique=True, verbose_name='Электронная почта')
    about_user = models.TextField(max_length=2000, verbose_name='Обо мне')
    image = models.ImageField(
        upload_to='avatar/',
        default='/avatar/default_photo/default_avatar.jpg',
        validators=[validate_avatar_size],
        blank=True,
        verbose_name='Аватар'
    )
    birthday = models.DateField(null=True, blank=True, verbose_name='День рождения')
    gender = models.CharField(max_length=55, choices=constants.GENDER, verbose_name='Пол')
    is_active = models.BooleanField('Активен', default=True)
    is_staff = models.BooleanField('Персонал', default=False)
    joined_date = models.DateTimeField('Дата регистрации', auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def get_full_name(self):
        full_name = '%s %s %s' % (self.firstname, self.lastname, self.email)
        return full_name.strip()

    def __str__(self):
        return self.email


# @receiver(pre_save, sender=User)
# def create_slug(sender, instance, **kwargs):
#     if not instance.url:
#         instance.url = slugify(instance.title)


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=4, verbose_name='Код')
    time = models.DateTimeField()

    def __str__(self):
        return f"{self.user}, {self.token}"


class Reviews(models.Model):
    title = models.CharField(max_length=1000, verbose_name='Комментарии')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review')
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class UserFavoriteAnime(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"

    def __str__(self):
        user_full_name = self.user.get_full_name()
        return f"{user_full_name} - {self.anime.translated_title}"
