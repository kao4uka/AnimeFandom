from django.urls import path
from apps.chats.consumers import ChatConsumer

websockets_urlpatterns = [
    path('api/v1/chat/', ChatConsumer.as_asgi()),
]