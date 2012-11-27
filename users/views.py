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

from srs.views import _collect_vocab


def user(request):
    user = request.user
    return _render(request, 'users/user.html', locals())


def user_vocab(request):
    user = request.user
    _update_crumbs(request)
    try:
        words = request.user.get_profile().get_personal_words()
    except:
        words = None
    title = "Your Vocabulary"
    
    if request.user.is_authenticated():
        _collect_vocab(request.user)
    return _render(request, 'users/user_vocab.html', locals())

def user_vocab_item(request, chars):
    
    return _render(request, 'users/user_vocab_item.html', locals())   
    
def user_articles(request):
    if request.user.is_authenticated():        
        articles = request.user.get_profile().get_personal_articles()        
        
    else:
        pass
    
    return _render(request, 'users/user_articles.html', locals())