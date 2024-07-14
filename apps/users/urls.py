from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.api import CustomTokenVerifyView, UserListApi, UserMeApi

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("verify/", CustomTokenVerifyView.as_view(), name="token_verify"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", UserMeApi.as_view(), name="user_me"),
    path("list/", UserListApi.as_view(), name="user_list"),
]
