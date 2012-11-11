#!/usr/bin/python
# -*- coding: utf8 -*-

import string, unicodedata
import redis
import os
PROJECT_PATH = os.path.normpath(os.path.dirname(__file__))

from redis_helper import get_redis

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





def _collect_vocab(user):
    
    # get the whole users' wordlist from redis:
    userkey = "PW:%s" % user.email
    r_server = get_redis()
    words = r_server.hgetall(userkey)
    
    # get any vocabulary that hasn't been tested before
    
    # get vocab that
    
    return vocablist