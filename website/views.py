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


from utils.helpers import _render, _is_english, _is_punctuation, _is_number, _split_unicode_chrs, _get_crumbs, _update_crumbs, _is_pinyin, _is_ambiguous, _convert_pinyin_to_numbered_notation
from utils.redis_helper import _get_redis, _search_redis, _add_to_redis, _increment_stats
import utils.messages as messages

from srs.views import _collect_vocab

from creader.views import _group_words

from cjklib import characterlookup
from cjklib.dictionary import *
from cjklib.reading import ReadingFactory
from fancy_cache import cache_page

from website.forms import SearchForm
from website.signals import *

def _problem(request, problem=None):    
    if request.is_ajax():
        html = render_to_string('website/problem_snippet.html', locals())
        url = '/problem/'
        #return HttpResponse(simplejson.dumps({'html':html, 'url':url}), mimetype="application/json")
        return HttpResponse(html)
    return _render(request, 'website/problem.html', locals())



def search(request, search_string=None, title='Search', words=None):
    
    
       
    # CHECK IF IT'S A POST REQUEST OR URL SEARCH
    if search_string == None:
        if request.method == 'POST':
            form = SearchForm(request.POST)
            if form.is_valid():
                _increment_stats('searches')
                search_string = form.cleaned_data['char']
                
        else:
            # NOT A POST AND NO SEARCH STRING - SHOW THEM THE PLAIN JANE SEARCH PAGE
            form = SearchForm()
            return _render(request, 'website/search.html', locals())

    if _is_ambiguous(search_string):
        
        return _problem(request, messages.AMBIGUOUS_WORD)
    
    
    if _is_pinyin(search_string):
        
                        
        # BUILD A PINYIN KEY # now replace spaces with underscores
        string = _convert_pinyin_to_numbered_notation(search_string).strip().replace(' ', '_')
        key = "PINYIN:%s" % string
        
        r_server = _get_redis()
        
        print key
        
        if filter(lambda x: x not in '12345', key) == key:
            key = "PINYIN:%s*" % string
            keys = r_server.keys(key)
            things = []
            for k in keys:
                object = _search_redis(k)['character_keys'].split(',')
                for o in object:
                    things.append(o)
                
        else:        
            try:
                things = _search_redis(key)['character_keys'].split(',')
            except:
                things = None
        
                        
        # FINALLY, LETS GET THE WORDS
        words = []
        if things:
            for x in things:
                word = _search_redis(x)
                try:
                    url = reverse('single_word', args=[word['chars']])
                    words.append(word)
                except:
                    pass
            
        return _render(request, 'website/wordlist.html', locals())
    
    
            
        

    # IF THE SEARCH IS ENGLISH, RETURN ERROR
    if _is_english(search_string):
        return _problem(request, messages.ENGLISH_WORD)

    # IF THE SEARCH IS OVER 10 CHARACTERS, RETURN A TEXT
    if len(search_string) > 12:
        from creader.views import text                
        return text(request, words=search_string)
    
          
    if not words:
        things = _split_unicode_chrs(search_string)
        words = _group_words(things)        
        _update_crumbs(request)

    # IF THE USER WAS LOGGED IN, RECORD IT IN THEIR 'SAVED WORDS'
    if request.user.is_authenticated():
        word_searched.send(
            sender=word_searched, 
            chars=search_string, 
            time=datetime.datetime.now(), 
            user_id=request.user.pk
        )
    
    title = "Search"
    subtitle = "%s" % search_string
        
    return _render(request, 'website/wordlist.html', locals())


def search_contains(request, search_string):
    
    key = "*C:*%s*" % search_string
    
    r_server = _get_redis()
    keys = r_server.keys(key)
    
    words = []
    for x in keys:
        word = _search_redis(x)
        try:
            url = reverse('single_word', args=[word['chars']])
            words.append(word)
        except:
            pass

    
    words =  sorted(words, reverse=False, key=lambda thing: len(thing))
    title = "Search"
    subtitle = "Showing %s words containing <strong>%s</strong>" % (len(words), search_string)
    _update_crumbs(request)
    
    return _render(request, 'website/wordlist.html', locals())


def search_beginning_with(request, search_string):
    key = "*C:%s*" % search_string
    r_server = _get_redis()
    keys = r_server.keys(key)
    
    words = []
    for x in keys:
        word = _search_redis(x)
        words.append(word)

    
    words =  sorted(words, reverse=False, key=lambda thing: len(thing))
    title = "Search"
    subtitle = "Showing words beginning with %s" % search_string
    _update_crumbs(request)
    
    return _render(request, 'website/wordlist.html', locals())     
    
            
def home(request):
    _update_crumbs(request)                
    return _render(request, 'website/home.html', locals())


# DISPLAYS A STATIC PAGE LIKE 'ABOUT' OR 'BOOKMARKLET'
def page(request, slug):
    template = 'website/pages/page.html'
    snippet = 'website/pages/%s.html' % slug
    _update_crumbs(request)
    
    return _render(request, template, locals(), page=slug)


    
def user(request):
    user = request.user
    return _render(request, 'website/user.html', locals())



# TODO - THIS SHOULD RETURN A GENERIC, NON-USER-SPECIFIC ARTICLE VIEW
def articles(request):
    return _render(request, 'website/articles.html', locals())


# DISPLAYS SITE STATISTICS
def stats(request):
    
    # TODO - do monthly filtering, backwards and forwards, comparisons etc.
    key = "stats:%s:%s" % (datetime.date.today().year, datetime.date.today().month)
    stats = _search_redis(key)
    
    return _render(request, 'website/stats.html', locals())    


# TODO - THIS SHOULD RETURN SOME KIND OF GENERIC WORDS VIEW
def words(request):
    return _render(request, 'website/wordlist.html', locals())

 
def get_personal_words(request):
    
    try:
        account = request.user.get_profile()
    except:
        return HttpResponse()
    
    
    # TODO - add pagination with django-endless maybe
    words = account.get_personal_words()
    if request.is_ajax():
        return HttpResponse(simplejson.dumps(words), mimetype="application/json")
    
    return _render(request, 'website/wordlist.html', locals())
    
    
    

    