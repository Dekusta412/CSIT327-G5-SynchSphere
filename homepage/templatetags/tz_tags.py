"""Template tags and filters for timezone handling"""
from django import template
from django.utils import timezone
import pytz

register = template.Library()


@register.filter
def convert_to_user_tz(dt, user):
    """
    Convert a UTC datetime to the user's timezone.
    Usage in template: {{ event.start_time|convert_to_user_tz:user }}
    """
    if dt is None or user is None:
        return dt
    
    try:
        # Get user profile to access their timezone
        profile = user.profile
        user_tz_name = profile.timezone
    except:
        user_tz_name = 'UTC'
    
    if user_tz_name is None:
        user_tz_name = 'UTC'
    
    # If datetime is naive, assume it's UTC
    if timezone.is_naive(dt):
        dt = pytz.UTC.localize(dt)
    
    # Convert to user's timezone
    user_tz = pytz.timezone(user_tz_name)
    return dt.astimezone(user_tz)
