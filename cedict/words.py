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


from cjklib import characterlookup
from cjklib.dictionary import *
from cjklib.reading import ReadingFactory




class Word(object):
    
    def __init__(self):
        # nothign to see here yet
        pass
    

class ChineseWord(Word):
    
    def __init__(self, chars=None):
        
        if chars:
            # derive the key
            self.key = "ZH:%sC:%s" % (len(chars), chars)
                        
            # get the object back from redis
            x = _search_redis(self.key)

            # fill in some values
            self.chars = chars
            self.length = len(chars)
            self.meanings = []
            
            # this next bit is a cluge, because the pronunciation/meanings are 
            # still hardcoded in the redis entries like this. Need to update the 
            # build_dictionary function 
            if 'pinyin1' in x:
                self.meanings.append({'pinyin': x['pinyin1'], 'meaning': x['meaning1']})
            if 'pinyin2' in x:
                self.meanings.append({'pinyin': x['pinyin2'], 'meaning': x['meaning2']})
            if 'pinyin3' in x:
                self.meanings.append({'pinyin': x['pinyin3'], 'meaning': x['meaning3']})
            if 'pinyin4' in x:
                self.meanings.append({'pinyin': x['pinyin4'], 'meaning': x['meaning4']})
            if 'pinyin5' in x:
                self.meanings.append({'pinyin': x['pinyin5'], 'meaning': x['meaning5']})


    def __unicode__(self):
        return self.chars
    
    def _get_random(self, number=1, chars=None, length='*'):
        """ Returns random words the same length as the character provided """
        
        if chars:
            length = len(chars)
        
        r_server = _get_redis()
        key = "ZH:%sC:*" % length

        randoms = []
        loop = 0
        for x in r_server.scan_iter(key):
            randoms.append(x)
            loop += 1
            if loop > 20:
                break
        
        random.shuffle(randoms,random.random)
                
        if number == 1:
            return _search_redis( randoms[0] )
        else:
            count = 0
            words = []
            while number > 0:
                words.append(_search_redis( randoms[count] ))
                count += 1
                number -= 1
            
            return words
        
        return
    
    def _contains(self, chars):
        """ Returns any words containing this word """
        
        r_server = _get_redis()
        key = "ZH:*C:*%s*" % chars        
        keys = r_server.scan_iter(key)
        

        words = []
        for x in keys:
            chars = x.split(':')[-1]
            if "，" in chars:
                continue
                
            new_word = ChineseWord(smart_unicode(chars))
            words.append(new_word)
            
        words =  sorted(words, reverse=False, key=lambda thing: thing.length)
        
        return words
        
    
    def _starts_with(self, chars):
        """
        Returns all words starting with these ones
        """
        
        r_server = _get_redis()
        key = "ZH:*C:%s*" % chars
        keys = r_server.scan_iter(key)

        words = []
        for x in keys:
            chars = x.split(':')[-1]
            if "，" in chars:
                continue
                
            new_word = ChineseWord(smart_unicode(chars))
            words.append(new_word)
            
        words =  sorted(words, reverse=False, key=lambda thing: thing.length)
        
        return words



