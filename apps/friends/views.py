from rest_framework import generics, permissions, exceptions
from rest_framework.response import Response
from rest_framework import status

from apps.friends.models import FriendRequest, FriendList
from apps.users.models import User
from apps.friends.serializers import (
    FriendRequestSerializer,
    FriendSerializer,
    DeclineFriendRequestSerializer,
    CancelFriendRequestSerializer

)
from apps.friends.services import (
    cancel_friend_request,
    add_friend,
    remove_friend,
    is_mutual_friend,
    decline_friend_request,
    accept_friend_request
)


class FriendListAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendSerializer

    def get_object(self):
        user_id = self.kwargs.get("user_id")

        try:
            friend_list = FriendList.objects.select_related('user').get(user=user_id)
        except FriendList.DoesNotExist:
            raise exceptions.NotFound('Такого пользователя не существует.')

        if self.request.user.id != user_id and not friend_list.friends.filter(pk=self.request.user.pk).exists():
            raise exceptions.PermissionDenied("Вы должны быть друзьями, чтобы просмотреть список друзей!")

        return friend_list


class FriendRequestAPIView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if self.request.user.id != int(user_id):
            raise exceptions.PermissionDenied("Вы не можете простматривать запросы другого пользователя!")
        return FriendRequest.objects.filter(receiver=self.request.user, is_active=True)


class SendFriendRequestAPIView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        user = request.user
        receiver_id = request.data.get('receiver')
        friend_list = FriendList.objects.filter(user=user, friends__id=receiver_id).exists()

        if receiver_id is None:
            return Response({'response': 'Поле "receiver" обязательно.'}, status=status.HTTP_400_BAD_REQUEST)

        if friend_list:
            return Response({'response': 'Этот пользователь уже в ваших друзьях.'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest.objects.filter(sender=user, receiver=receiver_id, is_active=True).exists()
        print(friend_request)
        if friend_request:
            return Response({'response': 'Вы уже отправили запрос в друзья.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        print(serializer)
        if serializer.is_valid(raise_exception=True):
            serializer.save(sender=user)
            return Response({'response': 'Запрос в друзья отправлен'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AcceptFriendRequestAPIView(generics.UpdateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'pk'
    lookup_url_kwarg = 'friend_request_id'

    def update(self, request, *args, **kwargs):
        user = self.request.user

        friend_request = self.get_object()
        if friend_request.receiver != user:
            return Response(
                {"response": "Этот запрос в друзья адресован другому пользователю."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not friend_request.is_active:
            return Response({'response': 'Этот запрос уже был обработан.'}, status=status.HTTP_400_BAD_REQUEST)

        accept_friend_request(friend_request)
        return Response({"response": "Запрос в друзья был принят."}, status=status.HTTP_200_OK)


class DeclineFriendRequestAPIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DeclineFriendRequestSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=kwargs)
        serializer.is_valid(raise_exception=True)

        user = self.request.user
        friend_request_id = serializer.validated_data.get('friend_request_id')

        try:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            if friend_request.receiver != user:
                return Response({"response": "Вы не можете отменить чужой запрос в друзья."},
                                status=status.HTTP_403_FORBIDDEN)

            friend_request.decline_friend_request()
            return Response({"response": "Запрос в друзья отклонен."}, status=status.HTTP_200_OK)
        except FriendRequest.DoesNotExist:
            return Response({"response": "Запрос в друзья не найден."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"response": f"Что-то пошло не так: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class RemoveFriendAPIView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CancelFriendRequestSerializer
    lookup_field = 'id'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.request.user
        remove_user = serializer.validated_data.get('receiver')

        try:
            friend_list = FriendList.objects.select_related('user').prefetch_related('friends').get(user=user)
        except FriendList.DoesNotExist:
            return Response({'response': 'Список друзей не найден для пользователя.'}, status=status.HTTP_404_NOT_FOUND)

        if is_mutual_friend(friend_list.friends.all(), remove_user):
            remove_friend(friend_list, remove_user)
            return Response({'response': "Пользователь успешно удален из друзей."}, status=status.HTTP_200_OK)

        return Response({'response': 'Пользователь не является вашим другом.'}, status=status.HTTP_400_BAD_REQUEST)


class CancelFriendRequestAPIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CancelFriendRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.request.user
        receiver = serializer.validated_data.get('receiver')

        if not receiver:
            return Response({'response': 'Получатель запроса не указан.'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest.objects.filter(sender=user, receiver=receiver, is_active=True)
        if not friend_request.exists():
            return Response({'response': 'Нет активных запросов в друзья.'}, status=status.HTTP_404_NOT_FOUND)

        for request_obj in friend_request:
            request_obj.cancel_friend_request()

        return Response({'response': 'Запрос в друзья отклонен.'}, status=status.HTTP_200_OK)
