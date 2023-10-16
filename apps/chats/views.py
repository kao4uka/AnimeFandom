from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.response import Response

from apps.chats.serializers import *
from apps.chats.models import *
from django.shortcuts import render


@login_required
def messages_page(request):
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chat_message_thread').order_by('timestamp')
    context = {
        'Threads': threads
    }
    return render(request, 'chat.html', context)

# class FriendRequestViewSet(viewsets.ModelViewSet):
#     queryset = FriendRequest.objects.all()
#     serializer_class = FriendRequestSerializer

    # def create(self, request):
    #     serializer = self.get_serializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save(sender=request.user)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
