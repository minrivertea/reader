#!/usr/bin/python
# -*- coding: utf8 -*-

import string, unicodedata
import redis
import os
PROJECT_PATH = os.path.normpath(os.path.dirname(__file__))

from utils.redis_helper import _get_redis

from urlparse import urlparse
from bs4 import BeautifulSoup
from readability.readability import Document

import uuid
import random
import re
import urllib2
import datetime
import time
from HTMLParser import HTMLParser

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

from cjklib import characterlookup
from cjklib.reading import ReadingFactory
from cjklib.dictionary import *

from utils.helpers import _render, _is_punctuation
from utils.redis_helper import _add_to_redis, _search_redis

def home(request):
    wordlist = _collect_vocab(request.user)     
    words = _cleanup_wordlist(request.user, wordlist['wordlist']).splitlines()
    already_tested = []
    ready_to_test = []
    for x in words:
        if int(x.split('/')[3]) == 0:
            ready_to_test.append(x)
        else:
            already_tested.append(x)
            
    rtt_count = len(ready_to_test)
    at_count = len(already_tested)
    
    return _render(request, 'srs/home.html', locals())


def _cleanup_wordlist(user, wordlist):
        
    new_list = []
    for x in wordlist.splitlines():
                
        key = "*C:%s" % x.split('/')[0]
                
        if x.split('/')[0] == '  ': 
            pass
        
        else:
                        
            try:
                _split_unicode_chrs(x.split('/')[0])
            except:
            
                try:
                    x.split('/')[3]
                except IndexError:
                    x = "".join((x, ' / 0'))
                    
                try:
                    x.split('/')[4]
                except IndexError:
                    x = "".join((x, ' / 0'))
                 
                try:
                    x.split('/')[5]
                except:
                    x = "".join((x, ' / None'))
                
                new_list.append(x)
    
    
    final = ""
    count = 1
    for x in new_list:
        if count == 1:
            final = "".join((final, x))
        else:
            final = "".join((final, ' \n', x))
            
        count += 1
     
    
    key = "PW:%s" % user.email
    values = {'wordlist': final,}
    _add_to_redis(key, values, user)
    
    return final

def _collect_vocab(user):
    
    # get the whole users' wordlist from redis:
    userkey = "PW:%s" % user.email
    r_server = _get_redis()
    words = r_server.hgetall(userkey)
        
    # get any vocabulary that hasn't been tested before
    
    # get vocab that
    
    return words