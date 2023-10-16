import os

from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')


from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
django_asgi_application = get_asgi_application()
from channels.auth import AuthMiddlewareStack


from apps.chats import routing


application = ProtocolTypeRouter(
    {
        'http': django_asgi_application,
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(
            URLRouter(
                routing.websockets_urlpatterns
            )))
    }
)
