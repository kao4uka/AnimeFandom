from datetime import timedelta
from config.settings.env_reader import env, csv

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG", cast=bool)
ALLOWED_HOSTS = env("ALLOWED_HOSTS", cast=csv())


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=3),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
