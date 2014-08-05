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

from website.signals import word_viewed 

  
from cedict.words import ChineseWord

def single_word(request, chars):
   
    word = ChineseWord(chars)
                    
    # chars = _split_unicode_chrs(smart_unicode(word['chars']))
    
    if request.user.is_authenticated():
        word_viewed.send(
                    sender=word_viewed, 
                    word=word, 
                    time=datetime.datetime.now(), 
                    user_id=request.user.email
                )
    
    return _render(request, 'cedict/single.html', locals())   




def get_examples(request, word):
    
    words = ChineseWord().starting_with(word)
    print words
        
    return _render(request, 'website/examples.html', locals())
    
