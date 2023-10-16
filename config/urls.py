from django.contrib import admin
from django.urls import path, include


from config.settings.base import DEBUG
from config.settings.drf_yasg import urlpatterns as doc_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/anime/', include('apps.anime.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/chat/', include('apps.chats.urls')),
    path('api/v1/friends/', include('apps.friends.urls')),
    path('', include('social_django.urls', namespace='social'))
]

urlpatterns += doc_urls

if DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]