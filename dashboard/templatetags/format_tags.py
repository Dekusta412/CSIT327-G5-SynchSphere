from django import template
from django.utils import timezone
from django.utils.timesince import timesince as dj_timesince
from django.template.defaultfilters import truncatechars
from dashboard.utils import get_timezone
import pytz

register = template.Library()


@register.simple_tag
def avatar_url(profile):
    """Return avatar URL or empty string if none."""
    if not profile:
        return ''
    try:
        if profile.avatar:
            return profile.avatar.url
    except Exception:
        pass
    return ''


@register.filter
def initials(user):
    """Return initials from first/last name or username."""
    if not user:
        return ''
    first = (user.first_name or '').strip()
    last = (user.last_name or '').strip()
    if first or last:
        return (first[:1] + (last[:1] if last else '')).upper()
    return (user.username[:2] or '').upper()


@register.filter
def format_dt(value, tz=None, fmt="%b %d, %Y %H:%M"):
    """Format a datetime for display; convert to tz if provided or use localtime."""
    if not value:
        return ''
    try:
        if tz:
            tzobj = get_timezone(tz)
            value = value.astimezone(tzobj)
        else:
            value = timezone.localtime(value)
        return value.strftime(fmt)
    except Exception:
        return str(value)


@register.filter
def timesince_short(value):
    """Return a short humanized "time since" string (e.g. "3 days ago")."""
    if not value:
        return ''
    try:
        delta = dj_timesince(value)
        return f"{delta} ago"
    except Exception:
        return ''


@register.filter
def truncate_chars(value, length=100):
    """Truncate text to a given number of characters."""
    if value is None:
        return ''
    try:
        return truncatechars(value, int(length))
    except Exception:
        return value
