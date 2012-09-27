#!/usr/bin/python
# -*- coding: utf8 -*-

import string, unicodedata
import redis
import os
PROJECT_PATH = os.path.normpath(os.path.dirname(__file__))

from redis_helper import get_redis

from bs4 import BeautifulSoup

from readability.readability import Document

import uuid
import re
import urllib2
import datetime
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
    # search
    d = getDictionary(dictionary, entryFactory=entry.UnifiedHeadword(), columnFormatStrategies={'Translation': TranslationFormatStrategy()})
    result = d.getFor(string, reading=reading)
    
    # shit... this only returns one translation, sometimes it's the wrong one.
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
                
        if unicodedata.category(x).startswith(('P', 'Z')):
            return True
    except:
        pass
    
    return False

def _is_number(x):
    
    try:
        float(x)
        return True
    except ValueError:
        return False

    if x.isdigit() or unicodedata.category(x).startswith('N'):
        return True
    
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
    if r_server.exists(key):
        return r_server.hgetall(key)
    else:
        return None
    

# TODO - there's a problem here. For example, some characters have multiple readings
# and so this function will only write the 1st reading, not subsequent ones. eg 都
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
            'id': uuid.uuid1().hex,
        }
        
        r_server.hmset(key, mapping)
        
    return True
    

# send me a dict of chars, and I'll return a dict of chars
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
        
        # if the character is English            
        if nc == False and _is_english(x):            
            obj['is_english'] = True
            english = True
            eng_word = x
            while english == True:
            
                # if the next character is also English, add it to this one
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

        
        
        if nc == True:
            if chinese_only == False:
                obj_list.append(obj)
                
            else:
                pass
                
            loop += 1
            continue

        word = None
        r = None
        i = 1
        search_string = x
                
        
        # at the end of this loop, we'll have a MULTI-CHAR-WORD or NONE
        while i > 0:
            try:
                next_char = chars[loop+i]
            except:
                break
                        
            if _is_punctuation(next_char):
                break
            
                        
            search_string = "%s%s" % (search_string, next_char)            
            key = "%sC:%s" % (len(search_string), search_string)
            r = search_redis(key) 
            
                    
            if r == None:
                break
            else:  
                word = r
                length = len(search_string)
                i += 1
            
        
        if word != None:
            # give X the values of the dictionary word
            for k, v in word.iteritems():
                obj[k] = v
                
                if k == 'chars':
                    obj[k] = x
                
                if k == 'pinyin1':
                    obj[k] = v.split()[0]
                    
            obj_list.append(obj)
            
            # if the word is more than 1 character, give the next X's the values too
            ni = 1
            while ni < length:
                
                n = {
                    'chars': chars[loop+ni],
                    'wordset': obj['wordset'],
                    'pinyin1': word['pinyin1'].split()[ni],
                }
                ni += 1
                obj_list.append(n)
            
            skip += (length-1)
            word = None
          
        # finally, if we have no WORD we'll just do a SINGLE-CHAR-LOOKUP
        else:
            key = "%sC:%s" % (len(x), x)
            r = search_redis(key)
            for k, v in r.iteritems():
                obj[k] = v
            obj_list.append(obj)
        
        loop += 1
     
    return obj_list                         




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

    if request.GET.get('url'):
        url = request.GET.get('url')


        # TODO if it's already been scanned and saved, don't bother parsing it again….

        html = urllib2.urlopen(url).read()
        
        text = readabilityParser(html)
        
        title = Document(html).title() 
        new_text = strip_tags(text)
        
        this_id = uuid.uuid1().hex
        key = "url:%s" % this_id
            
        mapping = {
            'user': 'dummy',
            'title': title, 
            'chars': new_text, 
            'timestamp': '12345',
            'hash': this_id,
            'url' : url,
        }
        
        r_server = redis.Redis("localhost")
        r_server.hmset(key, mapping)
        
        url = reverse('url', args=[this_id])
        return HttpResponseRedirect(url)


    if request.method == 'POST':
        form = CheckPinyinForm(request.POST)
        if form.is_valid():
            
            r_server = get_redis()
            if r_server.exists('stats'):
                r_server.hincrby('stats', 'searches', 1)
            else:
                mapping = {
                     'searches': 1,
                     'redis_hits': 1,   
                }
                r_server.hmset('stats', mapping)
            
            if request.user.is_authenticated() and len(form.cleaned_data['char']) < 10:
                word_searched.send(sender=word_searched, chars=form.cleaned_data['char'], time=datetime.datetime.now(), user_id=request.user.pk)
            
            if request.is_ajax():
                
                things = split_unicode_chrs(form.cleaned_data['char'])
                obj_list = group_words(things)
                
                return HttpResponse(simplejson.dumps(obj_list), mimetype="application/json")
            
            
            else:
                this_id = uuid.uuid1().hex
                key = "text:%s" % this_id
                
                mapping = {
                    'user': 'dummy', 
                    'chars': form.cleaned_data['char'], 
                    'timestamp': '12345',
                    'hash': this_id,
                }
                
                r_server = get_redis()
                r_server.hmset(key, mapping)
                url = reverse('text', args=[this_id])
            return HttpResponseRedirect(url)

            
    else:
        form = CheckPinyinForm()
        
    return render(request, 'website/home.html', locals())


# note that in this function, we are retrieving a text that has  
# already been stored and save in redis
def text(request, hashkey):
    
    key = 'text:%s' % hashkey
    
    r_server = get_redis()
    if r_server.exists(key):
        obj = r_server.hgetall(key)
    
    chars = obj['chars'].decode('utf-8') # because redis stores things as strings...
    things = split_unicode_chrs(chars)
    obj_list = group_words(things)
    
    return render(request, 'website/text.html', locals())


def url(request, hashkey):
    
    key = 'url:%s' % hashkey
        
    r_server = get_redis()
    if r_server.exists(key):
        obj = r_server.hgetall(key)
    
    title = obj['title']
    url = obj['url']
    chars = obj['chars'].decode('utf-8') # because redis stores things as strings...

    if request.is_ajax():
        things = split_unicode_chrs(chars)
        obj_list = group_words(things)
        
        return HttpResponse(simplejson.dumps(obj_list), mimetype="application/json")
    
    else:
        url = obj['url']
        uid = hashkey
    
    return render(request, 'website/text.html', locals())
    

def page(request, slug):
    template = 'website/%s.html' % slug
    
    if request.is_ajax():
        template = 'website/%s_snippet.html' % slug
        
        page = render_to_string(template, {'siteurl': RequestContext(request)['siteurl']})
        return HttpResponse(page)
            
    return render(request, template, locals())
    
def user(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'website/user.html', locals())


def stats(request):
    
    key = "stats"
    stats = search_redis(key)
    
    return render(request, 'website/stats.html', locals())    
    
    
def get_personal_words(request):
    try:
        account = request.user.get_profile()
    except:
        return HttpResponse()
    
    words = account.get_personal_words()
    
    if request.is_ajax():
        return HttpResponse(simplejson.dumps(words), mimetype="application/json")
    
    return render(request, 'website/vocab.html', locals())
    
    
    
    
    
    
    
    
    