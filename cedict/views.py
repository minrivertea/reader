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
  

def single_word(request, word):
   
    key = "ZH:%sC:%s" % (len(word), word)
    word = _search_redis(key)
            
    _update_crumbs(request, smart_unicode(word['chars']))
    crumbs = _get_crumbs(request)
    
    chars = _split_unicode_chrs(smart_unicode(word['chars']))
    
    title = "Search"
    url = reverse('search')

    if 'vocab' in request.path:
        url = reverse('vocab')
        title = "Vocabulary"

    return _render(request, 'cedict/single.html', locals())   




def get_examples(request, word):
    
    # FIRST CHECK IF THE WORD ALREADY HAS ANY EXAMPLES ATTACHED TO IT - IF YES, JUST RETURN THEM
    r_server = _get_redis()
    key = "ZH:%sC:%s" % (len(word), word)
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
    
