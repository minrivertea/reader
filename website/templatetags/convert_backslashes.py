# -*- coding: utf-8 -*-

from django import template


register = template.Library()



def convert_backslashes(value):
    """Converts a backslash into a <br/> tag"""


    new_value = value.replace('/', '<br/>')
     
        
    return new_value
    

register.filter('convert_backslashes', convert_backslashes)