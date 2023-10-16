from django.urls import path, include
from apps.users import views

urlpatterns = [
    path("sign_up/", views.UserRegistrationAPIView.as_view(), name="user-registration"),
    path("sign_up/checking-the-code/",
         views.UserRegisterCheckingTheCodeAPIView.as_view(),
         name="user-registration-checking-the-code"
         ),
    path("sign_in/", views.UserLoginAPIView.as_view(), name="user-authorization"),
    path("sign_out/", views.LogoutAPIView.as_view(), name="user-logout"),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/delete/', views.DeleteAccountView.as_view(), name='delete-account'),
    path("reset-password-email/", views.PasswordResetRequestAPIView.as_view(), name="search user and send mail"),
    path("reset-password-code/", views.PasswordResetCodeAPIView.as_view(), name="write code"),
    path("reset-new-password/<str:code>/", views.PasswordResetNewPasswordAPIView.as_view(), name="write new password")
]
