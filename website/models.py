#-*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

import datetime
import time
import unicodedata

from redis_helper import get_redis

from django.core.signals import request_finished
from django.utils.encoding import smart_str, smart_unicode

from website.signals import word_searched
from website.views import group_words, split_unicode_chrs, search_redis



# our main profile thing
class Account(models.Model):
    user = models.ForeignKey(User)
    date_joined = models.DateTimeField()
    words = models.TextField(blank=True) # CHARS / TIMESTAMP / VIEWCOUNT 
    articles = models.TextField(blank=True) # a list of article UIDs + timestamp + read/unread
    
    def __unicode__(self):
        return self.user.email
    
    def get_personal_words(self):
        
        r_server = get_redis()
        key = "PW:%s" % self.user.email
        wordlist = search_redis(key)['wordlist']
                
        obj_list = []
        
        for x in wordlist.splitlines():
            try:
                this_time = datetime.datetime.fromtimestamp(float(x.split('/')[1].strip(' ')))
                w = x.split('/')[0].strip(' ')
                key = "%sC:%s" % (len(smart_unicode(w)), w)
                word = search_redis(key)
                obj_list.append(dict(
                    chars=w, 
                    time=str(this_time.date()), 
                    count=x.split('/')[2],
                    pinyin=word['pinyin1'],
                    meaning=word['meaning1'],
                ))
            except:
                pass
        
        
        
        return obj_list
    
         

# SIGNAL HANDLERS!


# save a word in the user's personal wordlist
def save_word(sender, **kwargs):
    try:
        account = get_object_or_404(User, pk=kwargs['user_id']).get_profile()
    except:
        return 
    
    # words coming in need to be converted into unicode characters        
    things = split_unicode_chrs(kwargs['chars'])    
    obj_list = group_words(things, chinese_only=True)
                    
    r_server = get_redis()
    key = "PW:%s" % account.user.email
    
    this_users_words = ''
    if r_server.exists(key):
        this_users_words = search_redis(key)['wordlist']
        
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
        # if the word is already in the list, then remove it
        if smart_str(w) in smart_str(this_users_words):
            for line in smart_unicode(this_users_words).splitlines():
                if w == line.split('/')[0].strip():
                    to_remove.append(line)
                    count = int(line.split('/')[2]) + 1
                    

        # add / update the word
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