from django.urls import path
from apps.friends.views import *


urlpatterns = [
    path('send_friend_request/', SendFriendRequestAPIView.as_view(), name='send_friend_request'),
    path('accept_friend_request/<int:friend_request_id>/', AcceptFriendRequestAPIView.as_view(),
         name='accept-friend-request'),
    path('cancel_friend_request/', CancelFriendRequestAPIView.as_view(), name='cancel_friend_request'),
    path('decline_friend_request/<int:friend_request_id>/', DeclineFriendRequestAPIView.as_view(),
         name='decline_friend_request'),
    path('remove_friend/<int:id>/', RemoveFriendAPIView.as_view(), name='remove_friend'),
    path('friends/<int:user_id>/', FriendListAPIView.as_view(), name='friends_list'),
    path('friend_requests/<int:user_id>/', FriendRequestAPIView.as_view(), name='friend_requests'),
]

