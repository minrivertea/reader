#!/usr/bin/python
# -*- coding: utf8 -*-

import string, unicodedata
import redis
import os
PROJECT_PATH = os.path.normpath(os.path.dirname(__file__))


from urlparse import urlparse
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

from utils.helpers import _render, _is_english, _is_punctuation, _is_number, _split_unicode_chrs
from utils.redis_helper import _get_redis, _search_redis, _add_to_redis
import utils.messages as messages

from cjklib import characterlookup
from cjklib.dictionary import *
from cjklib.reading import ReadingFactory

from website.forms import SearchForm
from website.signals import *

from cedict.words import ChineseWord



# ACCEPTS A LIST OF CHARACTERS (a random search string perhaps) AND RETURNS A GROUPED LIST OF WORDS
def _group_words(chars, chinese_only=False):
    obj_list = []
    loop = 0        
    skip = 0

    for x in chars:
        
        if skip != 0:
            skip -= 1
            loop += 1
            continue
        
        obj = {
             'chars': x,
             'wordset': loop,   
        }
                
        nc = False
                
        # IS IT A LINEBREAK
        if nc == False and x == '\n':
            obj['is_linebreak'] = True
            nc = True

        # IS IT A SPACE    
        if nc == False and x == ' ':
            obj['is_space'] = True
            nc = True

        # IS IT PUNCTUATION
        if nc == False and _is_punctuation(x):
            obj['is_punctuation'] = True 
            nc = True
    
        
        # IS IT A NUMBER?          
        if nc == False and _is_number(x):
            obj['is_number'] = True
            number = True
            num = x
            while number == True:
            
                # if the next character is also a number, add it to this one
                try:
                    next = chars[loop+1]
                except:
                    break
                
                if _is_number(next):
                    num = "%s%s" % (num, next)
                    chars.pop(loop+1)

                else:
                    break
                            

            obj['chars'] = num
            nc = True
        
        
        
        
        # IS THE CHARACTER ENGLISH?            
        if nc == False and _is_english(x):            
            obj['is_english'] = True
            english = True
            eng_word = x
            while english == True:
            
                # IF THE NEXT CHAR IS ENGLISH, LETS BUILD THE ENGLISH WORD
                try:
                    next = chars[loop+1]
                except:
                    break
                
                if _is_english(next):
                    eng_word = "%s%s" % (eng_word, next)
                    chars.pop(loop+1)

                else:
                    break
                            

            obj['chars'] = eng_word
            nc = True
        
        # IF THE CHARACTER IS NOT CHINESE
        if nc == True:
            if chinese_only == False:
                obj_list.append(obj)
                
            loop += 1
            continue

        search_string = [x,]
                
        # THIS LOOP WILL BUILD OUR CHINESE WORD - GUESSING WE WON'T HAVE MANY MORE THAN 10 CHARS
        for i in range(1,10):
            try:
                next_chars = chars[loop+i]
                if _is_punctuation(next_chars):
                    next_chars = None
                    break
                else:
                    search_string.append(next_chars)
            except:
                break
        
        
        r_server = _get_redis()
        r = False   
        
        
        while r == False and len(search_string) > 0:            
            
            key = "ZH:%sC:%s" % ( len(search_string), "".join(search_string))
            r = r_server.exists(key)
            
            if r:
                break
            else:
                try:
                    search_string.pop()
                except IndexError:
                    pass
        

                
        # initialise a ChineseWord object and add it to our object_list
        the_string = "".join(search_string)
        word = ChineseWord(chars=the_string)
        obj_list.append(word)
        
        
        # tells us how many characters need to be skipped before we start searching again
        # because maybe this word included the subsequent 3 chars, so let's not searhc them
        # again
        skip += (len(search_string)-1)
        loop += 1
        
     
    return obj_list  
    
    
def readabilityParser(html):
    text = Document(html).summary()
    readable_title = Document(html).title()           
    return text

    
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
        
    def handle_data(self, d):
        self.fed.append(d)
        
    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
    
    


# USED FOR LONG DICTIONARY LOOKUPS, NOT FOR WEB ARTICLES
#def text(request, hashkey):
#    
#    key = 'text:%s' % hashkey
#    if _search_redis(key, lookup=False):
#        obj = _search_redis(key)
#    
#    chars = obj['chars'].decode('utf-8')
#    things = _split_unicode_chrs(chars)
#    obj_list = group_words(things)
#    title = 'Text'
#    
#    if request.is_ajax():
#        html = render_to_string('website/text_snippet.html', locals())
#        return HttpResponse(html)
#    
#    return _render(request, 'website/text.html', locals())


# RECEIVES A HASHKEY OR LIST OF WORDS AND RETURNS A FORMATTED HTML PAGE
def text(request, hashkey=None, words=None):
    
    if not hashkey:
        hashkey = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(5))
        key = "text:%s" % hashkey
    
        if request.user.is_authenticated():
            user = request.user.email
        else:
            user = 'anon'
            
        mapping = {
            'user': user,
            'title': '', 
            'chars': words,
            'timestamp': time.time(),
            'hash': hashkey,
            'url' : '',
        }
        
        # ADD IT TO REDIS
        r_server = _get_redis()
        r_server.hmset(key, mapping)
                        
    else:
        key = 'text:%s' % hashkey
    
    
    obj = None
    if _search_redis(key, lookup=False):
        obj = _search_redis(key)
    
    if not obj:
        problem = messages.NO_TEXT_FOUND
        if request.is_ajax():
            html = render_to_string('website/problem_snippet.html', locals())
            return HttpResponse(html)
        
        return _render(request, 'website/problem.html', locals())
    
    title = 'Article'
    try:
        url = urlparse(obj['url']).netloc
    except KeyError:
        pass
        
    chars = obj['chars'].decode('utf-8') # because redis stores things as strings...
    things = _split_unicode_chrs(chars)
    obj_list = _group_words(things) 
    
    
    list_template = 'creader/text_page_snippet.html' 
    
    if request.GET.get('page'):
        template = 'creader/text_page_snippet.html'
        return render_to_response(template, locals())
        
    return _render(request, 'creader/text.html', locals())
    
           
    
# HANDLES BOOKMARKLET REQUESTS
def url(request):
    # TODO if it's already been scanned and saved, don't bother parsing it again….
    
    if request.GET.get('url'):
        url = request.GET.get('url')
        
        # PARSE THE WEBPAGE AND RETURN A LIST OF CHARACTERS
        html = urllib2.urlopen(url).read()
        text = readabilityParser(html)
        title = Document(html).title() 
        new_text = strip_tags(text)
        
        # GIVE IT AN ID
        this_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(5))
        key = "text:%s" % this_id
    
        if request.user.is_authenticated():
            user = request.user.email
        else:
            user = 'anon'
            
        mapping = {
            'user': user,
            'title': title, 
            'chars': new_text,
            'timestamp': time.time(),
            'hash': this_id,
            'url' : url,
        }
        
        # ADD IT TO REDIS
        r_server = _get_redis()
        r_server.hmset(key, mapping)
        
        if request.user.is_authenticated():
            article_saved.send(sender=article_saved, article_id=this_id, time=time.time(), user_id=request.user.pk)
    
        return HttpResponseRedirect(reverse('text', args=[this_id]))
    else:
        
        problem = "TODO: Make a proper page here which explains the reader and how it works"
        return _render(request, 'website/problem.html', locals())  
    
    
    
    
    
    