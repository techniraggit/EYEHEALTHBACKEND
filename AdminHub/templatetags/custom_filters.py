# myapp/templatetags/custom_filters.py
from django import template
from django.utils import timezone
import pytz

register = template.Library()

@register.filter
def format_datetime(value, tz_name='Asia/Kolkata'):
    if value is None:
        return ''

    tz = pytz.timezone(tz_name)
    value = timezone.localtime(value, timezone=tz)

    return value.strftime("%B %d, %Y, %I:%M %p")

@register.filter(name='replace_underscore')
def replace_underscore(value):
    return value.replace('_', ' ')