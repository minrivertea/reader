#!/usr/bin/python
# -*- coding: utf8 -*-

import string, unicodedata
import redis

import datetime
import time
import json


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



from utils.helpers import _render, _is_english, _is_punctuation, _is_number, _split_unicode_chrs, _is_pinyin, _is_ambiguous, _normalize_pinyin, _pinyin_to_ascii
from utils.redis_helper import _get_redis, _search_redis, _add_to_redis
import utils.messages as messages


# APP
from creader.views import _group_words
from website.forms import SearchForm
from website.signals import *
from cedict.words import ChineseWord, EnglishWord
from users.models import User


from nginx_memcache.decorators import cache_page_nginx


@cache_page_nginx
def search(request, search_string=None, title='Search', words=None):
    
    r_server = _get_redis()
        
    # replace search string underscores with spaces
    if search_string:
        search_string = search_string.strip().replace('_', ' ')        
               

    # HANDLES EMPTY OR NULL SEARCH STRING
    if search_string == None and request.method != 'POST':
        form = SearchForm()
        return _render(request, 'website/search.html', locals())
          
          
    # CHECK IF IT'S A POST REQUEST OR URL SEARCH
    if search_string == None and request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search_string = form.cleaned_data['char']

        else:
            # POST AND NO SEARCH STRING - SHOW THEM THE PLAIN JANE SEARCH PAGE
            form = SearchForm()
            return _render(request, 'website/search.html', locals())


    # HANDLES AN AMBIGUOUS SEARCH
    if _is_ambiguous(search_string):
        return _problem(request, messages.AMBIGUOUS_WORD)

    # HANDLES A PINYIN SEARCH    
    if _is_pinyin(_pinyin_to_ascii(search_string)):
        return _pinyin_search(request, search_string)
    

    # IF THE SEARCH IS ENGLISH, RETURN ENGLISH
    if _is_english(search_string):
        key = settings.ENGLISH_WORD_KEY % (len(search_string.split(' ')), search_string)
        if r_server.exists(key):
            word = EnglishWord(words=search_string)
            words = word.characters
        return _render(request, 'website/wordlist.html', locals())


    # IF THE SEARCH IS OVER 10 CHARACTERS, RETURN A TEXT
    #if len(search_string) > 12:
    #    from creader.views import text                
    #    return text(request, words=search_string)
    
    
    if not words:
        things = _split_unicode_chrs(search_string)        
        words = _group_words(things)   

        
    # IF THE USER WAS LOGGED IN, RECORD IT IN THEIR 'SAVED WORDS'
    if request.user.is_authenticated():
        for x in words:
            word_searched.send(
                sender=word_searched, 
                word=x.chars, 
                time=datetime.datetime.now(), 
                user_id=request.user.email
            )
    
    
    # if there's only 1 word, take us straight to the single word definition
    if len(words) == 1:
        word = words[0]
        url = reverse('single_word', args=[word])
        return HttpResponseRedirect(url)
    
        
    return _render(request, 'website/wordlist.html', locals())


def _pinyin_search(request, search_string):
    
    # CLEAN UP THE INCOMING PINYIN
    clean_string = _normalize_pinyin(search_string)
    ascii_string = _pinyin_to_ascii(search_string)
    key = settings.PINYIN_WORD_KEY % ascii_string    
    
    suggested = []
    words = [] 
    r_server = _get_redis()    
    try:
        for o in json.loads(r_server.get(key)):
            word = ChineseWord(chars=o)
            for i in word.meanings:
                
                # IF THE CLEANED SEARCH STRING AND THE CONVERTED PINYIN MATCH
                if _normalize_pinyin(i['pinyin']) == clean_string:
                    words.append(word)
                    
                # IF THERE'S NO NUMBERS IN THE CLEANED_STRING, ADD IT
                elif not any(ext in clean_string for ext in ['1', '2', '3', '4', '5']):
                    words.append(word)
                
                else:
                    suggested.append(word)
    except TypeError:
        pass
                 
    return _render(request, 'website/wordlist.html', locals())
    

def search_contains(request, word):
    words = ChineseWord()._contains(word)    
    return _render(request, 'website/wordlist.html', locals())


def search_starts_with(request, word):
    words = ChineseWord()._starts_with(word)
    return _render(request, 'website/wordlist.html', locals())     
    
    
    
@cache_page_nginx        
def home(request):
    return _render(request, 'website/home.html', locals())


@login_required
@cache_page_nginx 
def stats(request):
    if not request.user.is_superuser:
        return _render(request, '500.html', locals())
        
    users = User.objects.all()
    return _render(request, 'website/stats.html', locals())


# DISPLAYS A STATIC PAGE LIKE 'ABOUT' OR 'BOOKMARKLET'
@cache_page_nginx
def page(request, slug):
    template = 'website/pages/%s.html' % slug
    return _render(request, template, locals())


 