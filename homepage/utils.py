"""Utility functions for dashboard app - optimized for performance"""
from django.core.cache import cache
from django.utils import timezone
from .models import UserProfile, Notification
import pytz

# Cache timezone objects to avoid repeated lookups
_timezone_cache = {}


def get_timezone(tz_string):
    """Get timezone object with caching"""
    if tz_string not in _timezone_cache:
        _timezone_cache[tz_string] = pytz.timezone(tz_string)
    return _timezone_cache[tz_string]


def get_user_profile(user):
    """Get or create user profile with caching"""
    cache_key = f'user_profile_{user.id}'
    profile = cache.get(cache_key)
    if profile is None:
        profile, created = UserProfile.objects.get_or_create(user=user)
        cache.set(cache_key, profile, 300)  # Cache for 5 minutes
    return profile


def get_unread_count(user):
    """Get unread notification count with caching"""
    cache_key = f'unread_count_{user.id}'
    count = cache.get(cache_key)
    if count is None:
        count = Notification.objects.filter(user=user, is_read=False).count()
        cache.set(cache_key, count, 60)  # Cache for 1 minute
    return count


def invalidate_user_cache(user_id):
    """Invalidate user-related cache"""
    cache.delete(f'user_profile_{user_id}')
    cache.delete(f'unread_count_{user_id}')


def convert_to_utc(dt, tz_name, treat_input_as_local=False):
    """Normalize a datetime to UTC, honoring the user's timezone preference.

    When treat_input_as_local is True we discard any existing tzinfo on the
    incoming datetime and interpret the raw clock time as being in the user's
    timezone (useful for HTML datetime-local inputs that Django parsed as UTC).
    """
    if dt is None:
        return None
    tz_name = tz_name or 'UTC'
    user_tz = get_timezone(tz_name)

    if treat_input_as_local:
        naive = dt.replace(tzinfo=None)
        localized = user_tz.localize(naive)
        return localized.astimezone(pytz.UTC)

    if timezone.is_naive(dt):
        localized = user_tz.localize(dt)
        return localized.astimezone(pytz.UTC)

    return dt.astimezone(pytz.UTC)
