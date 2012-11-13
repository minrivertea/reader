#-*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

import datetime
import time
import unicodedata
from urlparse import urlparse

from django.core.signals import request_finished
from django.utils.encoding import smart_str, smart_unicode

from website.signals import word_searched, article_saved
from creader.views import _group_words 
from utils.redis_helper import _search_redis, _get_redis
from utils.helpers import _split_unicode_chrs



# our main profile thing
class Account(models.Model):
    user = models.ForeignKey(User)
    date_joined = models.DateTimeField()
    
    def __unicode__(self):
        return self.user.email
    
    def get_personal_words(self):
        key = "PW:%s" % self.user.email
        wordlist = _search_redis(key)['wordlist']
                
        obj_list = []
        loop = 0
        for x in wordlist.splitlines():
            try:
                this_time = datetime.datetime.fromtimestamp(float(x.split('/')[1].strip(' ')))
                w = x.split('/')[0].strip(' ')
                key = "%sC:%s" % (len(smart_unicode(w)), w)
                word = _search_redis(key)
                word['time'] = str(this_time.date())
                word['count'] = x.split('/')[2]
                word['wordset'] = loop
                obj_list.append(word)
                loop += 1
            except:
                pass
        
        return obj_list
    
    def get_personal_articles(self):
        key = 'AL:%s' % self.user.email
        try:
            articleslist = _search_redis(key)['articlelist']
        except:
            articleslist = ''
        
        obj_list = []
        urls = []
        loop = 0
        for x in articleslist.split(','):
            key = "url:%s" % x.strip()
            a = _search_redis(key)
            try:
                if a['url'] in urls:
                    pass
                else:
                    urls.append(a['url'])
                    a['date'] = datetime.datetime.fromtimestamp(float(a['timestamp'].strip()))
                    a['shorturl'] = urlparse(a['url']).netloc
                    obj_list.append(a)
            except:
                pass
                
        return obj_list

    
         

# SIGNAL HANDLERS!

# SAVE AN ARTICLE IN THE USERS PERSONAL ARTICLE LIST:
def save_article(sender, **kwargs):
    try:
        account = get_object_or_404(User, pk=kwargs['user_id']).get_profile()
    except:
        return     
        
    r_server = _get_redis()
    key = "AL:%s" % account.user.email 
    
    if r_server.exists(key):
        current_list = _search_redis(key)['articlelist']
        
        new_value = ",".join((current_list, kwargs['article_id']))
    else:
        new_value = kwargs['article_id']
    
    
    mapping = {
        'articlelist': new_value,
    }
    
    r_server.hmset(key, mapping)
    
article_saved.connect(save_article)    
    
           


# save a word in the user's personal wordlist
def save_word(sender, **kwargs):
    try:
        account = get_object_or_404(User, pk=kwargs['user_id']).get_profile()
    except:
        return 
    
    # CLUGE THAT CONVERTS INCOMING CHARS INTO UNICODE        
    things = _|split_unicode_chrs(kwargs['chars'])    
    obj_list = group_words(things, chinese_only=True)
                    
    r_server = _get_redis()
    key = "PW:%s" % account.user.email
    
    this_users_words = ''
    if r_server.exists(key):
        this_users_words = _search_redis(key)['wordlist']
        
    loop = 0
    new_words = []
    to_remove = []
    output = ''
    for x in obj_list:
        
        # construct a word 
        w = smart_unicode(x['chars'])         
        additional = ''
        try:
            while obj_list[loop+1]['wordset'] == x['wordset']:                
                additional = "%s%s" % (additional, obj_list[loop+1]['chars'])
                obj_list.pop(loop+1)
            
                        
        except:
            pass
        
        
        w = "%s%s" % (w, additional)
        count = 1
        
        # IF THE WORD IS ALREADY IN THE LIST, REMOVE ITt
        if smart_str(w) in smart_str(this_users_words):
            for line in smart_unicode(this_users_words).splitlines():
                if w == line.split('/')[0].strip():
                    to_remove.append(line)
                    count = int(line.split('/')[2]) + 1
                    

        # ADD / UPDATE THE NEW WORD
        s = "%s / %s / %s\n" % (smart_str(w), time.time(), count)
        new_words.append(s)
        loop += 1
    
    
    for old in to_remove:
        this_users_words = smart_str(this_users_words).replace(smart_str(old), '')
            
    for new in new_words:
        this_users_words = "%s%s" % (new, this_users_words)
    
    
    mapping = {
        'wordlist': this_users_words,
    }
        
    r_server.hmset(key, mapping)        

word_searched.connect(save_word)