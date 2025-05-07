from django.urls import path
from .views import *
# from rest_framework_simplejwt.views import TokenRefreshView

# for JWT APRIL BRANCH
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # OLD URL ENDPOINT, WORKING
    # LOGIN WORKS FOR BOTH JWTs
    path('register/', UserRegistrationAPIView.as_view(), name='register-user'),
    path('login/', UserLoginAPIView.as_view(), name='login-user'),
    path('logout/', UserLogoutAPIView.as_view(), name='logout-user'),
    path('token/refresh',TokenRefreshView.as_view, name='token-refresh'),
    path('user/',UserInfoAPIView.as_view(), name='user-info'),
    
    # JWT BRANCH APRIL
    path('jwt/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
