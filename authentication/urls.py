from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView
from authentication.views import LogoutView, CustomTokenRefreshView


urlpatterns = [
    path('authentication/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('authentication/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('authentication/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('authentication/logout/', LogoutView.as_view(), name='auth_logout'),
]
