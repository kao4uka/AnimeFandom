from rest_framework import generics, permissions, exceptions
from rest_framework.response import Response
from rest_framework import status

from apps.users.models import User
from apps.friends.serializers import *
from apps.friends.models import *


class FriendListAPIView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FriendSerializer
    queryset = FriendList.objects.all()

    def get_object(self):
        user_id = self.kwargs.get("user_id")
        print(self.kwargs.get('user_id'))
        try:
            this_user = User.objects.get(pk=user_id)
            print(this_user)
        except User.DoesNotExist:
            raise exceptions.NotFound("Такого пользователя не существует!")

        try:
            friend_list = FriendList.objects.get(user=this_user)
        except FriendList.DoesNotExist:
            raise exceptions.NotFound(f"Не удалось найти список друзей для {this_user.username}")

        if self.request.user != this_user:
            if not self.request.user in friend_list.friends.all():
                raise exceptions.PermissionDenied("Вы должны быть друзьями, чтобы просмотреть список друзей!")

        return friend_list

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        friends = instance.friends.all()
        serializer = self.get_serializer(friends, many=True)
        return Response(serializer.data)


class FriendRequestAPIView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        account = User.objects.get(pk=user_id)
        if self.request.user != account:
            raise exceptions.PermissionDenied("Вы не можете простматривать запросы другого пользователя!")
        return FriendRequest.objects.filter(receiver=account, is_active=True)


class SendFriendRequestAPIView(generics.CreateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        user = request.user
        user_id = request.data.get('receiver')

        if user_id is None:
            return Response({'response': 'Поле "receiver" обязательно.'}, status=status.HTTP_400_BAD_REQUEST)

        receiver = User.objects.get(pk=user_id)

        friend_request = FriendRequest.objects.filter(sender=user, receiver=receiver, is_active=True)
        if friend_request.exists():
            return Response({'response': 'Вы уже отправили запрос в друзья.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
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

        friend_request.accept()
        return Response({"response": "Запрос в друзья был принят."}, status=status.HTTP_200_OK)


class RemoveFriendAPIView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CancelFriendRequestSerializer
    queryset = FriendList.objects.all()
    lookup_field = 'id'

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.request.user

        try:
            remove = serializer.validated_data.get('receiver')
            friend_list = FriendList.objects.get(user=user)
            friend_list.unfriend_user(remove)
            return Response({"response": "Пользователь успешно удален из друзей."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"response": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)
        except FriendList.DoesNotExist:
            return Response({"response": "Список друзей не найден для пользователя."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"response": f"Что-то пошло не так: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


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

            friend_request.decline()
            return Response({"response": "Запрос в друзья отклонен."}, status=status.HTTP_200_OK)
        except FriendRequest.DoesNotExist:
            return Response({"response": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"response": f"Что-то пошло не так: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


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
            request_obj.cancel()

        return Response({'response': 'Запрос в друзья отклонен.'}, status=status.HTTP_200_OK)
        # try:
        #     receiver = serializer.validated_data.get('receiver')
        #     friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver, is_active=True)
        #
        #     if not friend_requests.exists():
        #         return Response({"response": "У вас нет запросов в друзья."},
        #                         status=status.HTTP_404_NOT_FOUND)
        #
        #     # Cancel all active friend requests (in case there are multiple, although there shouldn't be)
        #     for request_obj in friend_requests:
        #         request_obj.cancel()
        #
        #     return Response({"response": "Запрос в друзья отклонен."}, status=status.HTTP_200_OK)
        # except User.DoesNotExist:
        #     return Response({"response": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)
        # except Exception as e:
        #     return Response({"response": f"Что-то пошло не так: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
