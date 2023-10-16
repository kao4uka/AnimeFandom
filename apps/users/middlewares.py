from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class CustomAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(
                request.resolver_match, 'func'
        ) and hasattr(
            request.resolver_match.func, 'permission_classes'
        ) and IsAuthenticated in request.resolver_match.func.permission_classes:
            user = request.user

            if not user.is_authenticated:
                return Response(
                    data={"detail": "Учетные данные не были предоставлены."},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        response = self.get_response(request)
        return response
