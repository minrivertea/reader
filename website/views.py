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
from cjklib.dictionary import CEDICT
from cjklib.reading import ReadingFactory

from website.forms import CheckPinyinForm
from website.signals import *


from re import compile as _Re
_unicode_chr_splitter = _Re( '(?s)((?:[\ud800-\udbff][\udc00-\udfff])|.)' ).split
def split_unicode_chrs(text):
    return [ chr for chr in _unicode_chr_splitter( text ) if chr ]



from cjklib.dictionary import *
from cjklib.reading import ReadingFactory

class TranslationFormatStrategy(format.Base):
    def format(self, string):
        try:
            new_string = string[0:string.index('CL:')] # take out the measure words
        except:
            new_string = string
            
        noslashes = new_string.strip('/') # strip the backslashes between meanings
        return noslashes



#render shortcut
def render(request, template, context_dict=None, **kwargs):
    return render_to_response(
        template, context_dict or {}, context_instance=RequestContext(request),
            **kwargs)        

def search(string, reading=None, dictionary='CEDICT'):
    d = getDictionary(dictionary, entryFactory=entry.UnifiedHeadword(), columnFormatStrategies={'Translation': TranslationFormatStrategy()})
    result = d.getFor(string, reading=reading)
    
    for x in result:
        if x.Translation is None:
            return None
        else:
            return dict(characters=x.HeadwordSimplified, meaning=x.Translation, pinyin=x.Reading)

def _is_punctuation(x):
    
    try:
        if x in string.whitespace:
            return True
            
        if x in string.punctuation:
            return True
                
        if unicodedata.category(x).startswith(('P', 'Z', 'S')):
            return True
            
            ENCLOSED_ALPHANUMERICS 
    except:
        pass
    
    return False

def _is_number(x):

    for t in x:
        
        if t.isdigit() or unicodedata.category(t).startswith('N'):
            return True
        
        try:
            float(t)
            return True
        except ValueError:
            return False
    
    return False




def _is_english(x):
    
    if len(x) > 1:
        for y in x:
            if y in string.ascii_letters:
                return True
    
    if x in string.ascii_letters:
        return True
    
    return False
    

def search_redis(key):
    r_server = get_redis()
    
    stats_key = "stats:%s:%s" % (datetime.date.today().year, datetime.date.today().month)    
    if r_server.exists(key):
        r_server.hincrby(stats_key, 'redis_hits', 1)
        return r_server.hgetall(key)
    
    else:
        return None
    

# ADDS A WORD TO REDIS FROM A DICTIONARY
def add_to_redis(key, values):

    
    r_server = get_redis()
    if r_server.exists(key):
        object = search_redis(key)
        count = (int(object['count']) + 1)
        new1 = "meaning%s" % count
        new2 = "pinyin%s" % count
        
        mapping = {
            new1: values['meaning'],
            new2: values['pinyin'], 
            'count': count,
        }
        
        r_server.hmset(key, mapping)
                
    else:
        mapping = {
            'chars': values['characters'],
            'pinyin1': values['pinyin'], 
            'meaning1': values['meaning'],
            'count': 1,
            'id': uuid.uuid4().hex,
        }
        
        r_server.hmset(key, mapping)
        
    return True
    

# ACCEPTS A LIST OF CHARACTERS (a random search string perhaps) AND RETURNS A GROUPED LIST OF WORDS
def group_words(chars, chinese_only=False):
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
                
        # if it's a line break
        if nc == False and x == '\n':
            obj['is_linebreak'] = True
            nc = True

            
        if nc == False and x == ' ':
            obj['is_space'] = True
            nc = True

            
        # if the character is punctuation
        if nc == False and _is_punctuation(x):
            obj['is_punctuation'] = True 
            nc = True
    
        
        # if the character is a number          
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
                
            else:
                pass
                
            loop += 1
            continue

        search_string = [x,]
        r_server = get_redis()
                
        # THIS LOOP WILL BUILD OUR CHINESE WORD - GUESSING WE WON'T HAVE MANY MORE THAN 5 CHARS
        for i in range(1,5):
            try:
                next_chars = chars[loop+i]
                if _is_punctuation(next_chars):
                    next_chars = None
                    break
                else:
                    search_string.append(next_chars)
            except:
                break
        
        
        r = False    
        while r == False:            
            key = "%sC:%s" % (len("".join(search_string)), "".join(search_string))
            r = r_server.exists(key)
            if r == True:
                break
            else:
                search_string.pop()

                
        
        key = "%sC:%s" % (len("".join(search_string)), "".join(search_string))
        word = search_redis(key)

        for k, v in word.iteritems():
            obj[k] = v        
        
        obj_list.append(obj)
        skip += (len(search_string)-1)
        
        loop += 1
    
    

     
    return obj_list                         

def main_search(request):
    
    if request.method == 'POST':
        form = CheckPinyinForm(request.POST)
        if form.is_valid():
            
            r_server = get_redis()
            
            # UPDATE THE STATS
            stats_key = "stats:%s:%s" % (datetime.date.today().year, datetime.date.today().month)
            if r_server.exists(stats_key):
                r_server.hincrby(stats_key, 'searches', 1)
                
            else:
                mapping = {
                     'searches': 1,
                     'redis_hits': 1,   
                }
                r_server.hmset(stats_key, mapping)
            
            
            # IF THE FORM IS LESS THAN 10 CHARACTERS
            if len(form.cleaned_data['char']) < 10:
                if request.user.is_authenticated():
                    word_searched.send(sender=word_searched, chars=form.cleaned_data['char'], time=datetime.datetime.now(), user_id=request.user.pk)
            
                if request.is_ajax():    
                    things = split_unicode_chrs(form.cleaned_data['char'])
                    obj_list = group_words(things)
                    
                    return HttpResponse(simplejson.dumps(obj_list), mimetype="application/json")
            
            # IF THERE'S LOTS OF TEXT SENT THROUGH, DO IT DIFFERENTLY
            else:
                
                # PREPARE SOME VARIABLES
                this_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(5))
                if request.user.is_authenticated():
                    account = request.user.email
                else:
                    account = 'anon'

                # ADD THIS TEXT TO REDIS
                key = "text:%s" % this_id
                mapping = {
                    'user': account, 
                    'chars': form.cleaned_data['char'], 
                    'timestamp': time.time(),
                    'hash': this_id,
                }
                r_server.hmset(key, mapping)
                
                if request.is_ajax():
                        things = split_unicode_chrs(form.cleaned_data['char'])
                        obj_list = group_words(things)
                        title = 'Text'
                        url = reverse('text', args=[this_id])
                        html = render_to_string('website/text_snippet.html', locals())
                        data = {
                            'html': html,
                            'url': url,
                        }
                        return HttpResponse(simplejson.dumps(data), mimetype="application/json") 
                else:
                    
                    # NOW REDIRECT TO THE TEXT FUNCTION, WHICH WILL RETRIEVE AND DISPLAY THE TEXT
                    url = reverse('text', args=[this_id])
                    return HttpResponseRedirect(url)

            
    else:
        form = CheckPinyinForm()
    
    
    return render(request, 'website/home.html', locals())
    
    
    


def search_word(request, word):
    
    things = split_unicode_chrs(word)
    words = group_words(things)
    _update_crumbs(request)
    title = "Search"
    search = True
    
    if request.user.is_authenticated():
        word_searched.send(sender=word_searched, chars=word, time=datetime.datetime.now(), user_id=request.user.pk)

    
    if request.is_ajax():
        html = render_to_string('website/vocab_snippet.html', locals())
        return HttpResponse(html)
    
    return render(request, 'website/vocab.html', locals())
   

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
            
            add_to_redis(key, dict(characters=new[1], pinyin=pinyin, meaning=meanings ))
                
    
    file.close()    
    return render(request, 'website/success.html', locals())      


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
           

def home(request):

    _update_crumbs(request)
    
    # HANDLES BOOKMARKLET REQUESTS
    if request.GET.get('url'):
        url = request.GET.get('url')

        # TODO if it's already been scanned and saved, don't bother parsing it again….
        
        
        # THIS PARSES THE WEBPAGE AND RETURNS A LIST OF CHARACTERS
        html = urllib2.urlopen(url).read()
        text = readabilityParser(html)
        title = Document(html).title() 
        new_text = strip_tags(text)
        
        
        # GIVE IT AN ID
        this_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(5))
        key = "url:%s" % this_id
        
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
        r_server = get_redis()
        r_server.hmset(key, mapping)
        
        article_saved.send(sender=article_saved, article_id=this_id, time=time.time(), user_id=request.user.pk)

        
        # NOW REDIRECT AND SERVE UP THE PAGE
        url = reverse('url', args=[this_id])
        return HttpResponseRedirect(url)

        
    return render(request, 'website/home.html', locals())



# USED FOR LONG DICTIONARY LOOKUPS, NOT FOR WEB ARTICLES
def text(request, hashkey):
    
    key = 'text:%s' % hashkey
    r_server = get_redis()
    if r_server.exists(key):
        obj = r_server.hgetall(key)
    
    chars = obj['chars'].decode('utf-8')
    things = split_unicode_chrs(chars)
    obj_list = group_words(things)
    title = 'Text'
    
    if request.is_ajax():
        html = render_to_string('website/text_snippet.html', locals())
        return HttpResponse(html)
    
    return render(request, 'website/text.html', locals())


# USED FOR WEB ARTICLES THAT COME THROUGH THE BOOKMARKLET
def url(request, hashkey):
    
    key = 'url:%s' % hashkey
    r_server = get_redis()
    if r_server.exists(key):
        obj = r_server.hgetall(key)
    
    title = 'Article' 
    url = urlparse(obj['url']).netloc
    chars = obj['chars'].decode('utf-8') # because redis stores things as strings...
    things = split_unicode_chrs(chars)
    obj_list = group_words(things)

    if request.is_ajax():
        html = render_to_string('website/text_snippet.html', locals())
        return HttpResponse(html)
    
    else:
        uid = hashkey
    
    return render(request, 'website/text.html', locals())
    

# DISPLAYS A STATIC PAGE LIKE 'ABOUT' OR 'BOOKMARKLET'
def page(request, slug):
    template = 'website/pages/page.html'
    snippet = 'website/pages/%s_snippet.html' % slug
    _update_crumbs(request)
    
    if request.is_ajax():
        
        page = render_to_string(snippet, {'siteurl': RequestContext(request)['siteurl']})
        return HttpResponse(page)
            
    return render(request, template, locals())


# CURRENTLY REDUNDANT    
def user(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'website/user.html', locals())



# GETS A LIST OF YOUR ARTICLES
def articles(request):
    
    if request.user.is_authenticated():        
        articles = request.user.get_profile().get_personal_articles()        
        
    else:
        pass
    
    if request.is_ajax():
    
        html = render_to_string('website/articles_snippet.html', locals())
        return HttpResponse(html)
    
    return render(request, 'website/articles.html', locals())

# DISPLAYS SITE STATISTICS
def stats(request):
    # TODO - do monthly filtering, backwards and forwards, comparisons etc.
    key = "stats:%s:%s" % (datetime.date.today().year, datetime.date.today().month)
    stats = search_redis(key)
    
    return render(request, 'website/stats.html', locals())    


# GENERATES A LIST OF USER'S PERSONAL VOCABULARY
def vocab(request):
    _update_crumbs(request)
    words = request.user.get_profile().get_personal_words()
    title = "Your Vocabulary"
    
    if request.is_ajax():
        html = render_to_string('website/vocab_snippet.html', locals())
        return HttpResponse(html)
    
    return render(request, 'website/vocab.html', locals())



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
    word = search_redis(key)
    
    _update_crumbs(request, smart_unicode(word['chars']))
    crumbs = _get_crumbs(request)
    
    chars = split_unicode_chrs(smart_unicode(word['chars']))
    
    title = "Search"
    url = reverse('search')

    if 'vocab' in request.path:
        url = reverse('vocab')
        title = "Vocabulary"

    
    if request.is_ajax():
        html = render_to_string('website/single_snippet.html', locals())
        return HttpResponse(html)

    return render(request, 'website/single.html', locals())    
    
def get_personal_words(request):
    
    try:
        account = request.user.get_profile()
    except:
        return HttpResponse()
    
    
    # TODO - add pagination with django-endless maybe
    words = account.get_personal_words()
    if request.is_ajax():
        return HttpResponse(simplejson.dumps(words), mimetype="application/json")
    
    return render(request, 'website/vocab.html', locals())
    
    
    
    
    
    
    
    
    