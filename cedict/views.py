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

from utils.helpers import _render, _is_english, _is_punctuation, _is_number, _split_unicode_chrs, _update_crumbs, _get_crumbs
from utils.redis_helper import _get_redis, _search_redis, _add_to_redis
import utils.messages as messages


from creader.views import _group_words

from cjklib import characterlookup
from cjklib.dictionary import *
from cjklib.reading import ReadingFactory

from website.forms import SearchForm
from website.signals import *
  
  

def copy_dictionary(request):
    # eg 一中一台 [yi1 Zhong1 yi1 Tai2] /first meaning/second meaning/
    file = open(settings.DICT_FILE_LOCATION)
    r_server = _get_redis()
    
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

            key = "%sC:%s" % ((len((new[1]))/3), new[1])
            


            if r_server.exists(key):
                object = _search_redis(key)
                try:
                    val = "meaning%s" % int(object['count']) + 1
                    object[val]
                except KeyError:
                    
                    count = (int(object['count']) + 1)
                    new1 = "meaning%s" % count
                    new2 = "pinyin%s" % count
                    
                    mapping = {
                        new1: meanings,
                        new2: pinyin, 
                        'count': count,
                    }
                    
                    r_server.hmset(key, mapping)
                        
            else:
                mapping = {
                    'chars': new[1],
                    'pinyin1': pinyin, 
                    'meaning1': meaning,
                    'count': 1,
                    'id': uuid.uuid4().hex,
                }
                
                r_server.hmset(key, mapping)
                

                
    
    file.close()    
    return _render(request, 'website/success.html', locals())      
    

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
    print key
    
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
    
    