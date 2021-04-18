from app_users.backends import EmailOrUsernameModelBackend
from django.contrib.auth.models import AbstractUser
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken


class UsernameOrPasswordAuthenticationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, allow_blank=False, required=False,
                                     allow_null=False, write_only=False, validators=[AbstractUser.username_validator])

    email = serializers.EmailField(allow_blank=False, allow_null=False, required=False, write_only=True)
    password = serializers.CharField(min_length=1, allow_null=False, required=True, write_only=True)

    class Meta:
        fields = (
            'email',
            'username',
            'password',
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if not attrs.get('email') and not attrs.get('username'):
            raise ValidationError({"message": "email or username is required for login"})

        custom_backend = EmailOrUsernameModelBackend()

        user = custom_backend.authenticate(request=self.context['request'], **attrs)

        if user is None or not user.is_active:
            raise AuthenticationFailed({'message': 'No active account found with the given credentials'})

        return self.get_token(user)

    @classmethod
    def get_token(cls, user):
        token = RefreshToken.for_user(user)
        return {
            'access': str(token.access_token),
            'refresh': str(token),
        }

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


__all__ = [
    'UsernameOrPasswordAuthenticationSerializer',
]
