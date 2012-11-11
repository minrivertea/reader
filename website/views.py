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

from utils.helpers import _render, _is_english, _is_punctuation, _is_number, _split_unicode_chrs
from utils.redis_helper import _get_redis, _search_redis, _add_to_redis
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
            
            stats_key = "stats:%s:%s" % (datetime.date.today().year, datetime.date.today().month)
            if _search_redis(stats_key, lookup=True):
                r_server = _get_redis()
                r_server.hincrby(stats_key, 'searches', 1)
            else:
                mapping = {
                     'searches': 1,
                     'redis_hits': 1,   
                }
                r_server.hmset(stats_key, mapping)
            
            search_string = form.cleaned_data['char']
    else:
        form = SearchForm()
    

    if len(search_string) < 10:
        if _is_english(search_string):
            problem = messages.ENGLISH_WORD
            if request.is_ajax():
                html = render_to_string('website/problem_snippet.html', locals())
                return HttpResponse(html)
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
    
    
   

def copy_dictionary(request):
    # eg 一中一台 [yi1 Zhong1 yi1 Tai2] /first meaning/second meaning/
    file = open('/home/ubuntu/django/reader/cedict_1_0_ts_utf-8_mdbg.txt')
    #file = open('/Users/chriswest/Desktop/django-code/reader/reader/cedict_1_0_ts_utf-8_mdbg.txt')
    count = 0
    
    for line in file:
        if line.startswith("#"):
            pass
        else:
            new = line.split()

            numbered_pinyin = line[(line.index('[')+1):(line.index(']'))]
            f = ReadingFactory()            
            pinyin =  f.convert(numbered_pinyin, 'Pinyin', 'Pinyin',
                sourceOptions={'toneMarkType': 'numbers', 'yVowel': 'v',
                'missingToneMark': 'fifth'})
            
            meanings = line[(line.index('/')+1):(line.rindex('/'))]

            # meanings = split((s.index('/') to last s.index('/')), '/') # this should give us a list of meanings ??
            key = "%sC:%s" % ((len((new[1]))/3), new[1])
            
            _add_to_redis(key, dict(characters=new[1], pinyin=pinyin, meaning=meanings ))
                
    
    file.close()    
    return _render(request, 'website/success.html', locals())      


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
        

def single_word(request, word):
   
    key = "%sC:%s" % (len(word), word)
    word = _search_redis(key)
    
    
    
    _update_crumbs(request, smart_unicode(word['chars']))
    crumbs = _get_crumbs(request)
    
    chars = _split_unicode_chrs(smart_unicode(word['chars']))
    
    title = "Search"
    url = reverse('search')

    if 'vocab' in request.path:
        url = reverse('vocab')
        title = "Vocabulary"

    
    if request.is_ajax():
        html = render_to_string('website/single_snippet.html', locals())
        return HttpResponse(html)

    return _render(request, 'website/single.html', locals())    
    
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
    
    
    
def get_examples(request, word):
    
    # FIRST CHECK IF THE WORD ALREADY HAS ANY EXAMPLES ATTACHED TO IT - IF YES, JUST RETURN THEM
    r_server = _get_redis()
    key = "%sC:%s" % (len(word), word)
    r = _search_redis(key)

    obj_list = []
    
    try:
        examples_list = r['examples']
        obj_list = examples_list.splitlines()
    except:
        examples_list = ''
    
    
    # IF THERE'S NO EXAMPLES YET, WE'LL CRAM IT FULL OF ANY REFERENCE WE CAN FIND
    if examples_list == '':
        all_url_keys = r_server.keys('url:*')
        for x in all_url_keys:
            text = r_server.hgetall(x)
            if smart_unicode(word) in smart_unicode(text['chars']):
                pos = smart_unicode(text['chars']).find(smart_unicode(word))
                new_string = "%s, %s, %s, %s \n" % (smart_unicode(text['chars'])[(pos-5):(pos+5)], x, text['url'], 1)
                obj_list.append(new_string)
            
        r_server.hset(key, 'examples', ("".join(obj_list))) 
      
     
    # FILTER EXAMPLES_LIST AND THEN RETURN A LIST OF EXAMPLES
    examples = []
    seen = []
    for x in obj_list:
        try:
            if x.split(', ')[0] not in seen:
                a = dict()
                a['snippet'] = x.split(', ')[0]
                a['source_key'] = x.split(', ')[1].split(':')[1]
                a['source_url'] = urlparse(x.split(', ')[2]).netloc
                a['rating'] = x.split(', ')[3]
                examples.append(a)
                seen.append(a['snippet'])
            else:
                pass
        except:
            pass
    
    examples =  sorted(examples, reverse=True, key=lambda thing: thing['rating'])
    
    if request.is_ajax():
        html = render_to_string('website/example_snippet.html', locals())
        return HttpResponse(html)
    
    return _render(request, 'website/examples.html', locals())
    

def get_similar(request, word):
    
    key = "*C:%s*" % word
    r_server = _get_redis()
    keys = r_server.keys(key)
    
    similar = []
    for x in keys:
        new = x.split(':')[1]        
        if smart_unicode(new) != word:
            similar.append(new)
    
    
    similar =  sorted(similar, reverse=False, key=lambda thing: len(thing))
    
    if request.is_ajax():
        html = render_to_string('website/similar_snippet.html', locals())
        return HttpResponse(html)
    
    return _render(request, 'website/similar.html', locals())    
    
    
    