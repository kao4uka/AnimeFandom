from rest_framework import generics, status, exceptions, response, permissions, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, hashers
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.db import IntegrityError
from django.utils import timezone
import random

from apps.users import serializers, models
from apps.users.models import User
from apps.users.services import GetLoginResponseService


class PasswordResetRequestAPIView(generics.CreateAPIView):
    """ API for search user and send mail with code """

    serializer_class = serializers.PasswordResetSearchUserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            email = serializer.validated_data["email"]
            user = models.User.objects.get(email=email)
        except:
            return response.Response(
                data={
                    "error": "Пользователь с указанным адресом электронной почты не найден."
                }, status=status.HTTP_404_NOT_FOUND
            )
        code = random.randint(1000, 10000)
        time = timezone.now() + timezone.timedelta(minutes=5)

        password_reset_token = models.PasswordResetToken(
            user=user, code=code, time=time
        )
        password_reset_token.save()

        send_mail(
            subject="Восстановление пароля",
            message=f"Код для восстановления пароля: {code} \n"
                    "Код действителен в течении 5 минут",
            from_email="end6999@gmail.com",
            recipient_list=[email],
        )

        return response.Response(data={"message": "Код был отправлен."}, status=status.HTTP_200_OK)


class PasswordResetCodeAPIView(generics.CreateAPIView):
    """ API для введения токена """

    serializer_class = serializers.PasswordResetCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            code = serializer.validated_data["code"]
            reset_code = models.PasswordResetToken.objects.get(
                code=code, time__gt=timezone.now()
            )
        except Exception as e:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data={
                    "error": f"Недействительный код для сброса пароля или время истечения кода закончилось.{e}"},
            )
        return response.Response(
            data={"detail": "success", "code": f"{code}"}, status=status.HTTP_200_OK)


class PasswordResetNewPasswordAPIView(generics.CreateAPIView):
    """ API для сброса пароля """

    serializer_class = serializers.PasswordResetNewPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        password_reset_token = get_object_or_404(models.PasswordResetToken,
                                                 code=request.data['code'])

        serializer.is_valid(raise_exception=True)
        user = password_reset_token.user
        password = serializer.validated_data["password"]
        user.password = hashers.make_password(password)
        user.save()

        password_reset_token.delete()

        return response.Response(
            data={"detail": "Пароль успешно сброшен."}, status=status.HTTP_200_OK)


class UserRegistrationAPIView(generics.CreateAPIView):
    """ API for user registrations """

    serializer_class = serializers.UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                user = models.User.objects.create_user(firstname=serializer.validated_data["firstname"],
                                                       lastname=serializer.validated_data["lastname"],
                                                       email=serializer.validated_data["email"],
                                                       nickname=serializer.validated_data['nickname'],
                                                       birthday=serializer.validated_data["birthday"],
                                                       gender=serializer.validated_data["gender"],
                                                       password=serializer.validated_data["password"],
                                                       )
                return response.Response(data=GetLoginResponseService.get_login_response(user, request))

            else:
                return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return response.Response(
                data={"detail": "Пользователь с данной электронной почтой существует!"}
            )


class UserRegisterCheckingTheCodeAPIView(generics.CreateAPIView):
    """ API для введения кода регистрации """

    serializer_class = serializers.PasswordResetCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            code = serializer.validated_data["code"]
            reset_code = models.PasswordResetToken.objects.get(
                code=code, time__gt=timezone.now()
            )

            # Проверка кода и завершение регистрации
            user = reset_code.user
            user.is_active = True
            user.save()

            # Удаление записи о коде
            reset_code.delete()

            return response.Response(
                data={"detail": "Регистрация успешно завершена"}, status=status.HTTP_200_OK
            )
        except models.PasswordResetToken.DoesNotExist:
            return response.Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data={
                    "error": "Недействительный код для регистрации или время истечения кода закончилось."
                },
            )


class UserLoginAPIView(generics.CreateAPIView):
    """ API for user sign in """

    serializer_class = serializers.UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(**serializer.validated_data)
        if not user:
            raise exceptions.AuthenticationFailed

        return response.Response(
            data=GetLoginResponseService.get_login_response(user, request)
        )


class LogoutAPIView(generics.CreateAPIView):
    """ API for user logout """

    serializer_class = serializers.LogoutSerailiser
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
            return response.Response(data={"detail": "Success"})
        except Exception as e:
            return response.Response(data={"error": f"{e}"}, status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        queryset = User.objects.all()
        return queryset


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class DeleteAccountView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
