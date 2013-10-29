#!/usr/bin/python
# -*- coding: utf8 -*-

import string, unicodedata
import os
PROJECT_PATH = os.path.normpath(os.path.dirname(__file__))

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils import simplejson



#render shortcut
def _render(request, template, context_dict=None, page=None, **kwargs):
    
    if request.is_ajax():
                
        if page:
            template = "".join((template.strip('page.html'), page, '.html'))
            
        else:
            template = template.replace('.html', "_snippet.html")
        
        html = render_to_string(
            template, 
            context_dict or {}, 
            context_instance=RequestContext(request),
            **kwargs
        )
        data = {'html': html, 'url': request.path}
        #return HttpResponse(simplejson.dumps(data), mimetype="application/json")
        
        return HttpResponse(html)

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



# RETURNS A NICELY FORMATTED HTML BREADCRUMB
def _get_crumbs(request):
    
    try:
        crumbs = request.session['crumbs']
    except:
        crumbs = ''
        request.session['crumbs'] = crumbs
        return crumbs
    
    items = []
    loop = 0
    objects = crumbs.split(' \ ')
    for x in objects:
        try:
            next = objects[loop+1]
            url = reverse('single_word', args=[x])
            string = '<a href="%s">%s</a>' % (url, x)
        except:
            string = x
        items.append(string)
        loop += 1
    
    crumbs_html = ' \ '.join(items) 
    return crumbs_html



# ADD OR REMOVE ITEMS FROM THE BREADCRUMB    
def _update_crumbs(request, word=None):
        
    try:
        crumbs = request.session['crumbs']
    except:
        crumbs = ''
        request.session['crumbs'] = crumbs
        return crumbs
    
    
    if word == None:
        crumbs = ''
        request.session['crumbs'] = crumbs
        return crumbs
    
    if word == crumbs.split(' \ ')[-1]:
        return crumbs
    
    match = False
    loop = 0
    for x in crumbs.split(' \ '):
        if word == x:
            match = True
            break
        else:
            match = False
            loop +1
            
    
    if match == True:
        head, sep, tail = crumbs.partition(word)
        new_crumb = "%s%s" % (head, sep)
    else:
        new_crumb = "%s \ %s" % (crumbs, word)
    
    request.session['crumbs'] = new_crumb
    return new_crumb
        

