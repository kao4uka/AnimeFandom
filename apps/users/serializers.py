from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from apps.users.models import *
from apps.friends.models import *


class PasswordResetNewPasswordSerializer(serializers.Serializer):
    code = serializers.IntegerField(min_value=1000, max_value=9999)
    password = serializers.CharField(
        style={"input_type": "password"}, min_length=4
    )


class PasswordResetCodeSerializer(serializers.Serializer):
    code = serializers.CharField()


class PasswordResetSearchUserSerializer(serializers.Serializer):
    email = serializers.CharField()

    def validate_email(self, email):
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return ValidationError(
                f"Пользователь с указанным адресом электронной почты не найден."
            )
        return email


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("firstname", "lastname", "email", "birthday", "gender", "password")


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(
        style={"input_type": "password"}, help_text="min length 3", min_length=3
    )


class LogoutSerailiser(serializers.Serializer):
    refresh = serializers.CharField()


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ('title', 'datetime', 'user',)


class UserProfileSerializer(serializers.ModelSerializer):
    review = ReviewSerializer(many=True)

    class Meta:
        model = User
        fields = ['image', 'firstname', 'lastname', 'gender', 'birthday', 'review']

    def update(self, instance, validated_data):
        instance.firstname = validated_data.get('firstname', instance.firstname)
        instance.lastname = validated_data.get('lastname', instance.lastname)
        instance.image = validated_data.get('image', instance.image)
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.save()
        return instance
