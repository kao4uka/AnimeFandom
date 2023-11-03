from django.db import models

from config.settings.base import AUTH_USER_MODEL


class FriendList(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, related_name='user', on_delete=models.CASCADE, verbose_name='Пользователь')
    friends = models.ManyToManyField(AUTH_USER_MODEL, blank=True, related_name='friend_list', verbose_name='Друг')

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = 'Друг'
        verbose_name_plural = 'Друзья'


class FriendRequest(models.Model):
    sender = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='receiver')
    is_active = models.BooleanField(blank=True, null=True, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.email} -> {self.receiver.email}'

    class Meta:
        verbose_name = 'Запрос в друзья'
        verbose_name_plural = 'Запросы в друзья'
