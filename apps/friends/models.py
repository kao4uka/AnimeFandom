from django.db import models

from config.settings.base import AUTH_USER_MODEL


class FriendList(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, related_name='user', on_delete=models.CASCADE, verbose_name='Пользователь')
    friends = models.ManyToManyField(AUTH_USER_MODEL, blank=True, related_name='friend_list', verbose_name='Друг')

    def __str__(self):
        return self.user.get_full_name()

    def add_friend(self, user):
        if self.user and user and not user in self.friends.all():
            self.friends.add(user)

    def remove_friend(self, user):
        if user in self.friends.all():
            self.friends.remove(user)

    def unfriend_user(self, remove):
        remover_friend_list = self
        remover_friend_list.remove_friend(remove)

        friend_list = FriendList.objects.get(user=remove)
        friend_list.remove_friend(remover_friend_list.user)

    def is_mutual_friend(self, friend):
        if friend in self.friends.all():
            return True
        return False

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

    def accept(self):
        if self.sender == self.receiver:
            return f'{self.sender} не может принять запрос в друзья от самого себя!'
        receiver_friend_list, created = FriendList.objects.get_or_create(user=self.receiver)
        if created:
            receiver_friend_list.add_friend(self.sender)
        sender_friend_list, created = FriendList.objects.get_or_create(user=self.sender)
        if created:
            sender_friend_list.add_friend(self.receiver)
        self.is_active = False
        self.save()

    def decline(self):
        self.is_active = False
        self.save()

    def cancel(self):
        self.is_active = False
        self.save()

    class Meta:
        verbose_name = 'Запрос в друзья'
        verbose_name_plural = 'Запросы в друзья'


