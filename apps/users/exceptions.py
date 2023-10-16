from rest_framework.exceptions import APIException


class AlreadyInFavoritesError(APIException):
    status_code = 400
    default_detail = 'Аниме уже добавлено в избранное. Вы не можете добавить его снова.'
    default_code = 'already_in_favorites'


class AnimeNotFoundError(APIException):
    status_code = 404
    default_detail = 'Аниме не найдено или не удалено. Пожалуйста, убедитесь, что аниме существует и опубликовано.'
    default_code = 'anime_not_found'
