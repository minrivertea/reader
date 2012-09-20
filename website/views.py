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


from cjklib import characterlookup
from cjklib.dictionary import CEDICT
from cjklib.reading import ReadingFactory

from website.forms import CheckPinyinForm


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
        if len(x) > 1:
            return True
        
        if x in string.whitespace:
            return True
            
        if x in string.punctuation:
            return True
        
        if x.isdigit():
            return True
        
        if unicodedata.category(x).startswith(('P', 'Z', 'N')):
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
    


def add_to_redis(key, values):
    
    if search_redis(key) is None:
    
        mapping = {
            'pinyin': values['pinyin'], 
            'characters': values['characters'], 
            'meaning': values['meaning'],
            'id': uuid.uuid1().hex,
        }
        r_server = get_redis()
        r_server.hmset(key, mapping)
        
    return True
    

def group_words(chars):
    # send me a dict of chars, and I'll return a dict of chars
    
    obj_list = []
    loop = 0
    
    for x in chars:
        obj_list.append(dict(
            character=x,
            pinyin=None,
            meaning=None,
            is_english=False,
            is_punctuation=False,
            is_linebreak=False,
            wordset=loop,
        ))
        loop += 1
   
    
    loop = 0
    skip = 0
    
    for x in obj_list:
        if skip == 0:
            
            # is it a punctuation mark? if so ignore it
            if _is_punctuation(x['character']):
                x['is_punctuation'] = True                
            
            if _is_number(x['character']):
                x['is_number'] = True 
                try:
                    if _is_number(obj_list[loop+1]['character']):
                        newvalue = (x['character'] + obj_list[loop+1]['character'])
                        x['character'] = newvalue
                        x['is_number'] = True
                        obj_list.pop(loop+1)
                except:
                    pass
                    
            if x['character'] == '\n':
                x['is_linebreak'] = True
                if obj_list[loop+1]['character'] == '\n':
                    obj_list.pop(loop+1)
            
            
            if _is_english(x['character']):
                x['is_english'] = True
                eng = True                    
                while (eng == True):
                    count = 1
                    try:
                        if _is_english(obj_list[loop+count]['character']):
                            newvalue = (x['character'] + obj_list[loop+count]['character'])
                            x['character'] = newvalue
                            x['is_english'] = True
                            obj_list.pop(loop+1)
                            count += 1
                        
                        else:
                            eng = False
                        
                    except:
                        pass
            
            else:
                d = None
                c = None
                b = None
                a = x['character']
                r = None # the final word
                
                
                # this next block just checks "is there a next character?"
                # and also "is it punctuation?"
                try:
                    if _is_punctuation(obj_list[loop+1]['character']): 
                        b = None
                    else:     
                        b = (x['character'] + obj_list[loop+1]['character'])



                    if b:
                        try:
                            c = (b + obj_list[loop+2]['character'])
                            if _is_punctuation(obj_list[loop+2]['character']):
                                c = None
                            
                            if c:
                                try:
                                    d = (c + obj_list[loop+3]['character'])
                                    if _is_punctuation(obj_list[loop+3]['character']): 
                                        d = None
                                except:
                                    pass       
                        except:
                            pass              
                except:
                    pass
                
                if b:
                    key = "2CHARS:%s" % b
                    if search_redis(key):
                        r = search_redis(key)

                    
                    if r:
                        obj_list[loop+1]['wordset'] = x['wordset']
                        x['meaning'] = r['meaning']
                        x['pinyin'] = r['pinyin'].split()[0]
                        obj_list[loop+1]['pinyin'] = r['pinyin'].split()[1] 
                        r = None
                        skip += 1
    
                                    
                if c and skip > 0:
                    key = "3CHARS:%s" % c
                    if search_redis(key):
                        r = search_redis(key)
                    
    
                    if r:
                        obj_list[loop+2]['wordset'] = x['wordset']
                        obj_list[loop+1]['wordset'] = x['wordset']
                        x['meaning'] = r['meaning']
                        x['pinyin'] = r['pinyin'].split()[0]
                        obj_list[loop+1]['pinyin'] = r['pinyin'].split()[1]
                        obj_list[loop+2]['pinyin'] = r['pinyin'].split()[2]
                        r = None
                        skip += 1
    
    
                if d and skip > 0:
                    key = "4CHARS:%s" % d
                    if search_redis(key):
                        r = search_redis(key)
                        

    
                    if r:
                        obj_list[loop+3]['wordset'] = x['wordset']
                        obj_list[loop+2]['wordset'] = x['wordset']
                        obj_list[loop+1]['wordset'] = x['wordset']
                        
                        x['meaning'] = r['meaning']
                        x['pinyin'] = r['pinyin'].split()[0]
                        obj_list[loop+1]['pinyin'] = r['pinyin'].split()[1]
                        obj_list[loop+2]['pinyin'] = r['pinyin'].split()[2]
                        obj_list[loop+3]['pinyin'] = r['pinyin'].split()[3]
                        r = None
                        skip += 1
    
                
                if skip == 0: # just a check to see if we've had any luck with 2, 3 or 4 chars...
                    key = "1CHARS:%s" % a
                    if search_redis(key):
                        r = search_redis(key)
                        x['meaning'] = r['meaning'] 
                        x['pinyin'] = r['pinyin']


                
        else:
            skip -= 1

        loop += 1
     
    return obj_list                         



def group_words_backwards(chars):
    # different from above, this works through the text backwards. 
    # in theory, it should more reliably find words. 
    
    obj_list = []
    loop = 0
    
    
    # I don't think I need to loop this two times - can't I loop through on the next bit?
    for x in chars:
        obj_list.append(dict(
            character=x,
            pinyin=None,
            meaning=None,
            is_english=False,
            is_punctuation=False,
            wordset=loop,
        ))
        loop += 1
   
    
    loop = 0
    skip = 0
    
    for x in obj_list:
        if skip == 0:
            # is it a punctuation mark? if so ignore it
            if _is_punctuation(x['character']):
                x['is_punctuation'] = True
                
        
            
            if _is_number(x['character']):
                x['is_number'] = True    
                try:
                    if _is_number(obj_list[loop+1]['character']):
                        newvalue = (x['character'] + obj_list[loop+1]['character'])
                        x['character'] = newvalue
                        x['is_number'] = True
                        obj_list.pop(loop+1)
                except:
                    pass

            else:
            
                d, c, b = None
                a = x['character']
                r = None # the final word
                
                try:
                    if _is_punctuation(obj_list[loop+1]['character']): 
                        b = None
                    else:     
                        b = (x['character'] + obj_list[loop+1]['character'])

                    if b:
                        try:
                            c = (b + obj_list[loop+2]['character'])
                            if _is_punctuation(obj_list[loop+2]['character']):
                                c = None
                            
                            if c:
                                try:
                                    d = (c + obj_list[loop+3]['character'])
                                    if _is_punctuation(obj_list[loop+3]['character']): 
                                        d = None
                                except:
                                    pass       
                        except:
                            pass              
                except:
                    pass
                
                if b:
                    key = "2CHARS:%s" % b
                    if search_redis(key):
                        r = search_redis(key)

                    
                    if r:
                        obj_list[loop+1]['wordset'] = x['wordset']
                        x['meaning'] = r['meaning']
                        x['pinyin'] = r['pinyin'].split()[0]
                        obj_list[loop+1]['pinyin'] = r['pinyin'].split()[1] 
                        r = None
                        skip += 1
    
                                    
                if c and skip > 0:
                    key = "3CHARS:%s" % c
                    if search_redis(key):
                        r = search_redis(key)

    
                    if r:
                        obj_list[loop+2]['wordset'] = x['wordset']
                        obj_list[loop+1]['wordset'] = x['wordset']
                        x['meaning'] = r['meaning']
                        x['pinyin'] = r['pinyin'].split()[0]
                        obj_list[loop+1]['pinyin'] = r['pinyin'].split()[1]
                        obj_list[loop+2]['pinyin'] = r['pinyin'].split()[2]
                        r = None
                        skip += 1
    
    
                if d and skip > 0:
                    key = "4CHARS:%s" % d
                    if search_redis(key):
                        r = search_redis(key)
                        


    
                    if r:
                        obj_list[loop+3]['wordset'] = x['wordset']
                        obj_list[loop+2]['wordset'] = x['wordset']
                        obj_list[loop+1]['wordset'] = x['wordset']
                        
                        x['meaning'] = r['meaning']
                        x['pinyin'] = r['pinyin'].split()[0]
                        obj_list[loop+1]['pinyin'] = r['pinyin'].split()[1]
                        obj_list[loop+2]['pinyin'] = r['pinyin'].split()[2]
                        obj_list[loop+3]['pinyin'] = r['pinyin'].split()[3]
                        r = None
                        skip += 1
    
                
                if skip == 0: # just a check to see if we've had any luck with 2, 3 or 4 chars...
                    key = "1CHARS:%s" % a
                    if search_redis(key):
                        r = search_redis(key)
                        x['meaning'] = r['meaning'] 
                        x['pinyin'] = r['pinyin']


                
        else:
            skip -= 1

        loop += 1
     
    return obj_list   



def copy_dictionary(request):
    # eg 一中一台 一中一台 [yi1 Zhong1 yi1 Tai2] /first meaning/second meaning/
    file = open('/home/ubuntu/django/reader/cedict_1_0_ts_utf-8_mdbg.txt')
    
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
            key = "%sCHARS:%s" % ((len((new[1]))/3), new[1])
            
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
            
            this_id = uuid.uuid1().hex
            key = "text:%s" % this_id
            
            mapping = {
                'user': 'dummy', 
                'chars': form.cleaned_data['char'], 
                'timestamp': '12345',
                'hash': this_id,
            }
            
            r_server = redis.Redis("localhost")
            r_server.hmset(key, mapping)
            
            if request.is_ajax():
                
                things = split_unicode_chrs(form.cleaned_data['char'])
                obj_list = group_words(things)
                
                return HttpResponse(simplejson.dumps(obj_list), mimetype="application/json")
            
            url = reverse('text', args=[this_id])
            return HttpResponseRedirect(url)

            
    else:
        form = CheckPinyinForm()
        
    return render(request, 'website/home.html', locals())


def text(request, hashkey):
    
    key = 'text:%s' % hashkey
    
    r_server = redis.Redis("localhost")
    if r_server.exists(key):
        obj = r_server.hgetall(key)

    
    chars = obj['chars'].decode('utf-8') # because redis stores things as strings...
    things = split_unicode_chrs(chars)
    obj_list = group_words(things)
    
    return render(request, 'website/text.html', locals())


def url(request, hashkey):
    
    key = 'url:%s' % hashkey
        
    r_server = redis.Redis("localhost")
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
    

def about(request):
    
    if request.is_ajax():
      
        return HttpResponse('website/about.html')
            
    return render(request, 'website/about.html', locals())