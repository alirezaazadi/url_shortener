from app_users.serializers import UsernameOrPasswordAuthenticationSerializer
from rest_framework_simplejwt.views import TokenViewBase


class CustomTokenObtainPairView(TokenViewBase):
    serializer_class = UsernameOrPasswordAuthenticationSerializer


__all__ = [
    'CustomTokenObtainPairView',
]
