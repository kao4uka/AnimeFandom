from django.db import models
from django.contrib.auth import get_user_model

from apps.chats.managers import ThreadManager

User = get_user_model()


class Thread(models.Model):
    first_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='thread_first_person')
    second_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='thread_second_person')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    class Meta:
        unique_together = ['first_person', 'second_person']


class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, blank=True, null=True, related_name='chat_message_thread')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(max_length=2000)
    timestamp = models.DateTimeField(auto_now_add=True)

