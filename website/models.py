#-*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

import datetime

from django.core.signals import request_finished
from django.utils.encoding import smart_str, smart_unicode

from website.signals import word_searched
from website.views import group_words, split_unicode_chrs



# our main profile thing
class Account(models.Model):
    user = models.ForeignKey(User)
    date_joined = models.DateTimeField()
    words = models.TextField(blank=True) # a list of word UIDs + timestamp 
    articles = models.TextField(blank=True) # a list of article UIDs + timestamp + read/unread
    
    def __unicode__(self):
        return self.user.email
    
    def get_personal_words(self):
                
        newlist = self.words.splitlines() 
        obj_list = []
        for x in newlist:
            obj_list.append(x.split('/')[0])
        
        
        return obj_list
        


# SIGNAL HANDLERS!


# save a word in the user's personal wordlist
def save_word(sender, **kwargs):

    try:
        account = get_object_or_404(User, pk=kwargs['user_id']).get_profile()
    except:
        return 
    things = split_unicode_chrs(kwargs['chars'])
    obj_list = group_words(things, chinese_only=True)
            
    loop = 0
    w = ''
    s = ''
    
    # account.words = ''
    
    for x in obj_list:
                
        w = x['chars']
        
        try:
            while obj_list[loop+1]['wordset'] == x['wordset']:
                w += obj_list[loop+1]['chars']
                obj_list.pop(loop+1)
        except:
            pass
        
        s = "%s / %s \n" % (w, datetime.datetime.now())
        s.encode('utf-8')
        account.words = "%s%s" % (account.words, s)
        loop +=1 
    
    account.save()    
    
word_searched.connect(save_word)