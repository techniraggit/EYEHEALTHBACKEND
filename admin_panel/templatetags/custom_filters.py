from django import template
from django.utils import timezone
import pytz

register = template.Library()


@register.filter(name="format_datetime")
def format_datetime(value, tz_name="Asia/Kolkata"):
    if value is None:
        return ""

    tz = pytz.timezone(tz_name)
    value = timezone.localtime(value, timezone=tz)

    return value.strftime("%B %d, %Y, %I:%M %p")


@register.filter(name="replace_underscore")
def replace_underscore(value, separator: str = " "):
    return value.replace("_", separator)


@register.filter(name="replace_comma")
def replace_comma(value, separator: str):
    return value.replace(",", separator)

@register.filter(name="truncate_chars")
def truncate_chars(value, max_length=75):
    if len(value) > max_length:
        return value[:max_length] + '...'
    return value

@register.filter(name="remove_comma_from_days_left")
def remove_comma_from_days_left(value):
    return str(value).split(',')[0]

from utilities.core import encode_data
@register.filter(name="encode_base64")
def encode_base64(value):
    return encode_data(value)