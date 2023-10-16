from django.core.exceptions import ValidationError


def upload_to_image(instance, filename):
    ext = filename.split('.')[-1]
    new_name = f'{instance.original_title}.{ext}'
    return f'anime_images/{new_name}'


def upload_to_episode(instance, filename):
    ext = filename.split('.')[-1]
    new_name = f"{instance.episode_number}_{instance.episode_title}.{ext}"
    return f"anime_videos/{instance.season.id}/{new_name}"


def validate_image_size(value):
    file_size = value.size
    limit = 4 * 1024 * 1024  # 4 MB
    if file_size > limit:
        raise ValidationError('Файл слишком большой! Размер не должен превышать 4 МБ.')
