from rest_framework import serializers

from apps.friends.models import FriendRequest, FriendList
from apps.friends.services import is_mutual_friend


class CancelFriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('receiver', 'receiver_id')


class DeclineFriendRequestSerializer(serializers.Serializer):
    friend_request_id = serializers.IntegerField()


class FriendSerializer(serializers.ModelSerializer):
    is_mutual = serializers.SerializerMethodField()

    class Meta:
        model = FriendList
        fields = ('id', 'user', 'is_mutual')

    def get_is_mutual(self, obj):
        user = self.context['request'].user
        user_data = obj.user
        auth_user_friend_list = FriendList.objects.get(user=user)
        return is_mutual_friend(auth_user_friend_list, obj)


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('id', 'sender', 'receiver', 'is_active', 'timestamp')
