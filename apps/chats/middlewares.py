# import jwt
# from django.contrib.auth import get_user_model

# from django.contrib.auth.models import AnonymousUser
# from channels.db import database_sync_to_async
# from channels.middleware import BaseMiddleware
# from django.db import close_old_connections
# from jwt import InvalidTokenError
# from django.conf import settings
# from datetime import datetime
#
# User = get_user_model()
#
# django.setup()
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
#
#
# ALGORITHM = "HS256"
#
#
# @database_sync_to_async
# def get_user(token):
#     try:
#         payload = jwt.decode(token, settings.base.SECRET_KEY, algorithms=ALGORITHM)
#         print('payload', payload)
#     except InvalidTokenError:
#         print('no payload')
#         return AnonymousUser()
#
#     token_exp = datetime.fromtimestamp(payload['exp'])
#     if token_exp < datetime.utcnow():
#         print("no date-time")
#         return AnonymousUser()
#
#     try:
#         user = User.objects.get(id=payload['user_id'])
#         print('user', user)
#     except User.DoesNotExist:
#         print('no user')
#         return AnonymousUser()
#
#     return user
#
#
# class TokenAuthMiddleware(BaseMiddleware):
#     async def __call__(self, scope, receive, send):
#         close_old_connections()
#         try:
#             authorization_header = scope.get('headers', []).get(b'authorization', None)
#             if authorization_header:
#                 token = authorization_header.decode('utf-8').split('Bearer ')[-1]
#         except ValueError:
#             token = None
#
#         scope['user'] = await get_user(token)
#         return await super().__call__(scope, receive, send)
#
#
# def JwtAuthMiddlewareStack(inner):
#     return TokenAuthMiddleware(inner)
