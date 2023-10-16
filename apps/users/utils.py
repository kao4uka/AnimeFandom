import random
import string

from django.core.exceptions import ValidationError


def random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def upload_to_avatar(instance, filename):
    ext = filename.split('.')[-1]
    new_name = f'{instance.nickname}.{ext}'
    return f'users_avatar/{new_name}'


def validate_avatar_size(value):
    file_size = value.size
    limit = 5 * 1024 * 1024  # 5 MB
    if file_size > limit:
        raise ValidationError('Файл слишком большой! Размер не должен превышать 4 МБ.')

