from django.urls import path
from apps.anime import views


urlpatterns = [
    path('list/', views.AnimeListAPIView.as_view(), name='get_anime_list'),
    path('<slug:url>/episode/<int:episode_number>/',
         views.AnimeEpisodeDetailAPIView.as_view(),
         name='get_anime_episode_detail'),
    path('<int:anime_id>/', views.AnimeDetailAPIView.as_view(), name='get_anime_detail'),
    path('status/', views.AnimeStatusAPIView.as_view({'get': 'list'}), name="anime-status"),
    path('status/<int:id>/', views.AnimeStatusDetailAPIView.as_view(), name="anime-status"),
    path('favorites/', views.FavoriteListAPIView.as_view(), name='favorites-list'),
    path('favorites/add/<int:anime_id>/', views.AddToFavoritesAPIView.as_view(), name='add-to-favorites'),
    path('favorites/remove/<int:anime_id>/', views.RemoveFromFavoritesAPIView.as_view(), name='remove-from-favorites'),
]
