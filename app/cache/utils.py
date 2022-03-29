import string
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone


def create_random_string(length):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))


def create_ttl():
    return timezone.now() + timedelta(seconds=settings.CACHE_ITEM_TTL)
