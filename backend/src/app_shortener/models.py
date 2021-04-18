import uuid

import architect
import base62
from app_shortener.utilities import generate_random_string
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.timezone import now

User = get_user_model()


@architect.install(feature='partition', **{'type': 'range', 'subtype': 'string_firstchars',
                                           'constraint': '1', 'column': 'short_url'})
class URLMap(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    short_url = models.CharField('short url', max_length=8, primary_key=True)
    original_url = models.TextField('original url')

    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    thirty_days_ago_check_date = models.DateTimeField(default=None, null=True)
    seven_days_ago_check_date = models.DateTimeField(default=None, null=True)
    current_day_check_date = models.DateTimeField(default=None, null=True)

    cached_statistics = models.JSONField(default=dict)

    @staticmethod
    def _rebuild_user_string(base_string, frame_length):
        return f'{base_string[:-frame_length]}{get_random_string(frame_length, allowed_chars=base62.CHARSET_DEFAULT)}'

    def _create_salted_url(self):
        return f'{self.original_url}{uuid.uuid1()}'

    def _build_short_url(self, *args, **kwargs):
        salted_string = self._create_salted_url()
        short_url = self.short_url
        total_acceptable_tries = 200
        user_tries = 0

        while total_acceptable_tries:
            try:
                self.short_url = generate_random_string(original_string=salted_string, base_string=short_url)
                return super().save(*args, **kwargs)
            except:  # noqa
                total_acceptable_tries -= 1

                if user_tries < 10:
                    if short_url:
                        user_tries += 1
                        short_url = self._rebuild_user_string(base_string=short_url, frame_length=user_tries)
                    else:
                        salted_string = self._create_salted_url()
                else:
                    short_url = None

    def save(self, *args, **kwargs):
        if not self.created_at:
            self._build_short_url(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return self.short_url


@architect.install(feature='partition', **{'type': 'range', 'subtype': 'string_firstchars',
                                           'constraint': '1', 'column': 'url'})
class History(models.Model):
    class Platform(models.TextChoices):
        MOBILE = ('Mobile', 'Mobile')
        PC = ('PC', 'PC')
        OTHER = ('Other', 'Other')

    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    url = models.ForeignKey('URLMap', on_delete=models.SET_NULL, null=True)

    platform = models.TextField(default=Platform.PC, choices=Platform.choices, max_length=8)
    browser = models.CharField(max_length=128)

    created_at = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-created_at']

        indexes = [
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.url} visited at {self.created_at} in {self.browser}"


__all__ = [
    'URLMap',
    'History',
]
