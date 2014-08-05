from django import template
import datetime
import ast

register = template.Library()

@register.filter
def convert_timestamp(value):
    """Converts a timestamp to a datetime"""
    datetime_value = datetime.datetime.fromtimestamp(float(value))    
    return datetime_value