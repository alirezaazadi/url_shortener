from app_shortener.models import URLMap
from app_shortener.validators import short_url_validator
from rest_framework import serializers


class CreateShortURLSerializer(serializers.ModelSerializer):
    short_url = serializers.CharField(max_length=8, min_length=8, required=False, validators=[short_url_validator])
    original_url = serializers.CharField(required=True)

    class Meta:
        model = URLMap
        fields = [
            'short_url',
            'original_url'
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs['user'] = self.context['request'].user
        return attrs
