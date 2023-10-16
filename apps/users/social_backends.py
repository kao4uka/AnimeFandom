from django.contrib.auth import get_user_model
from social_core.backends.google import GoogleOAuth2

User = get_user_model()


class CustomGoogleOAuth2(GoogleOAuth2):
    def user_data(self, access_token, *args, **kwargs):
        user_data = super(CustomGoogleOAuth2, self).user_data(access_token, *args, **kwargs)

        # Получение email из данных пользователя
        email = user_data.get('email', None)

        if email:
            # Проверка, есть ли пользователь с таким email
            user, created = User.objects.get_or_create(email=email, defaults={'username': email})

            if created:
                # Устанавливаем случайный пароль
                password = User.objects.make_random_password()
                user.set_password(password)
                user.save()

        return user_data
