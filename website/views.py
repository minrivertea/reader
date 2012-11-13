#!/usr/bin/python
# -*- coding: utf8 -*-

import string, unicodedata
import redis
import os
PROJECT_PATH = os.path.normpath(os.path.dirname(__file__))

from urlparse import urlparse

import uuid
import random
import re
import urllib2
import datetime
import time

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils import simplejson
from django.template.loader import render_to_string
from django.utils.encoding import smart_str, smart_unicode

from utils.helpers import _render, _is_english, _is_punctuation, _is_number, _split_unicode_chrs, _get_crumbs, _update_crumbs
from utils.redis_helper import _get_redis, _search_redis, _add_to_redis, _increment_stats
import utils.messages as messages


from creader.views import _group_words

from cjklib import characterlookup
from cjklib.dictionary import *
from cjklib.reading import ReadingFactory

from website.forms import SearchForm
from website.signals import *
  

def search(request, search_string=None):
    
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            
            _increment_stats('searches')
            
            search_string = form.cleaned_data['char']
    else:
        form = SearchForm()
    

    if len(search_string) < 10:
        if _is_english(search_string):
            problem = messages.ENGLISH_WORD
            if request.is_ajax():
                html = render_to_string('website/problem_snippet.html', locals())
                url = '/problem/'
                
                return HttpResponse(simplejson.dumps({'html':html, 'url':url}), mimetype="application/json")
            return _render(request, 'website/problem.html', locals())

        things = _split_unicode_chrs(search_string)
        words = _group_words(things)
        _update_crumbs(request)
        title = "Search"
        search = True

        if request.user.is_authenticated():
            word_searched.send(sender=word_searched, chars=search_string, time=datetime.datetime.now(), user_id=request.user.pk)
        
        if request.is_ajax():
            html = render_to_string('website/vocab_snippet.html', locals())
                                
            url = "/search/%s" % search_string
            data = {'html': html, 'url': url}
            return HttpResponse(simplejson.dumps(data), mimetype="application/json")
        
        return _render(request, 'website/vocab.html', locals())
    
    # IF IT'S OVER 10 CHARACTERS, HANDLE LIKE A TEXT
    else:
        
        from creader.views import text                
        return text(request, words=form.cleaned_data['char'])

    
    return _render(request, 'website/home.html', locals())
    

def home(request):
    _update_crumbs(request)                
    return _render(request, 'website/home.html', locals())



# DISPLAYS A STATIC PAGE LIKE 'ABOUT' OR 'BOOKMARKLET'
def page(request, slug):
    template = 'website/pages/page.html'
    snippet = 'website/pages/%s_snippet.html' % slug
    _update_crumbs(request)
    
    if request.is_ajax():
        
        page = render_to_string(snippet, {'siteurl': RequestContext(request)['siteurl']})
        return HttpResponse(page)
            
    return _render(request, template, locals())


# CURRENTLY REDUNDANT    
def user(request, pk):
    user = get_object_or_404(User, pk=pk)
    return _render(request, 'website/user.html', locals())



# GETS A LIST OF YOUR ARTICLES
def articles(request):
    
    if request.user.is_authenticated():        
        articles = request.user.get_profile().get_personal_articles()        
        
    else:
        pass
    
    if request.is_ajax():
    
        html = render_to_string('website/articles_snippet.html', locals())
        return HttpResponse(html)
    
    return _render(request, 'website/articles.html', locals())

# DISPLAYS SITE STATISTICS
def stats(request):
    # TODO - do monthly filtering, backwards and forwards, comparisons etc.
    key = "stats:%s:%s" % (datetime.date.today().year, datetime.date.today().month)
    stats = _search_redis(key)
    
    return _render(request, 'website/stats.html', locals())    


# GENERATES A LIST OF USER'S PERSONAL VOCABULARY
def vocab(request):
    _update_crumbs(request)
    try:
        words = request.user.get_profile().get_personal_words()
    except:
        words = None
    title = "Your Vocabulary"
    
    if request.is_ajax():
        html = render_to_string('website/vocab_snippet.html', locals())
        return HttpResponse(html)
    
    return _render(request, 'website/vocab.html', locals())

 
def get_personal_words(request):
    
    try:
        account = request.user.get_profile()
    except:
        return HttpResponse()
    
    
    # TODO - add pagination with django-endless maybe
    words = account.get_personal_words()
    if request.is_ajax():
        return HttpResponse(simplejson.dumps(words), mimetype="application/json")
    
    return _render(request, 'website/vocab.html', locals())
    
    
    

    