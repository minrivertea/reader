# -*- coding: utf-8 -*-

from django import template
from django.utils.encoding import smart_str, smart_unicode



register = template.Library()



def highlight_keyword(value, arg):
    """Highlights a particular character in a given string"""
 
    new = "<strong>%s</strong>" % arg
    new_string = value.replace(smart_str(arg), smart_str(new))
            
    return new_string
    

register.filter('highlight_keyword', highlight_keyword)