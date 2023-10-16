from django.urls import path
from apps.chats.views import *

urlpatterns = [
    path('', messages_page),
]