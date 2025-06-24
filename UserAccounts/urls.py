from django.urls import path
from .views import *
# from rest_framework_simplejwt.views import TokenRefreshView

# for JWT APRIL BRANCH
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

urlpatterns = [
    # Replace the existing token obtain pair view with our custom one
    path('jwt/register/', UserRegistrationAPIView.as_view(), name='register'),
    path('jwt/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # New endpoint for user profile
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    
    # New endpoint for profile updates
    path('profile/update/', UserProfileUpdateView.as_view(), name='user-profile-update'),
    
    # New endpoint for admin profile updates
    path('users/<int:user_id>/update/', UserProfileAdminUpdateView.as_view(), name='user-profile-admin-update'),
    
    # New endpoint for updating user by record ID
    path('users/record/<int:record_id>/update/', UserProfileByIDUpdateView.as_view(), name='user-profile-by-id-update'),
    # endpoint to update own account
    path('profile/update-credentials/', UserCredentialsUpdateView.as_view(), name='user-update-credentials'),
    # endpoint for superuser admin to update any user's password and username
    path('users/<int:user_id>/update-password/', AdminPasswordUpdateView.as_view(), name='admin-update-user-password'),
    # List all users based on roles and permission
    path('users/', UserListView.as_view(), name='user-list'),

# endpoints to manage accounts status
# GET List all account status history
path('account-status/history/', AccountStatusHistoryView.as_view(), name='account-status-history'),
# PUT/PATCH
path('users/<int:user_id>/change-status/', AccountStatusChangeView.as_view(), name='account-status-change'),
# Get account status history for a specific user
path('users/<int:user_id>/account-status/history/', UserAccountStatusHistoryView.as_view(), name='user-account-status-history'),
# allow a user view own account status history
path('account-status/my-history/', OwnAccountStatusHistoryView.as_view(), name='own-account-status-history'),
# Get account status details by record ID
path('account-status/<int:record_id>/', AccountStatusDetailView.as_view(), name='account-status-detail'),

# List all login history with statistics
path('login-history/', LoginHistoryListView.as_view(), name='login-history-list'),

# Get login history for a specific user
path('users/<int:user_id>/login-history/', UserLoginHistoryView.as_view(), name='user-login-history'),
]
