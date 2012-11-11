#!/usr/bin/python
# -*- coding: utf8 -*-

import string, unicodedata
import os
PROJECT_PATH = os.path.normpath(os.path.dirname(__file__))

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext



#render shortcut
def _render(request, template, context_dict=None, **kwargs):
        
    return render_to_response(
        template, context_dict or {}, context_instance=RequestContext(request),
            **kwargs)  


from re import compile as _Re
_unicode_chr_splitter = _Re( '(?s)((?:[\ud800-\udbff][\udc00-\udfff])|.)' ).split
def _split_unicode_chrs(text):
    return [ chr for chr in _unicode_chr_splitter( text ) if chr ]


def _is_punctuation(x):
    
    try:
        if x in string.whitespace:
            return True
            
        if x in string.punctuation:
            return True
                
        if unicodedata.category(x).startswith(('P', 'Z', 'S')):
            return True
            
    except:
        pass
    
    return False

def _is_number(x):

    for t in x:
        
        if t.isdigit() or unicodedata.category(t).startswith('N'):
            return True
        
        try:
            float(t)
            return True
        except ValueError:
            return False
    
    return False


def _is_english(x):
    
    if len(x) > 1:
        for y in x:
            if y in string.ascii_letters:
                return True
    
    if x in string.ascii_letters:
        return True
    
    return False

