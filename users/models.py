#-*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,\
    PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from django.core.mail import send_mail

from django.shortcuts import get_object_or_404

import datetime
import time
import unicodedata
import json
import uuid
from urlparse import urlparse

from django.utils.encoding import smart_unicode

from website.signals import word_searched, word_viewed
from utils.redis_helper import _get_redis
from cedict.words import ChineseWord


class CustomUserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = CustomUserManager.normalize_email(email)
        user = self.model(username=email, email=email,
                          is_staff=False, is_active=True, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        username = email
        u = self.create_user(username, email, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u


class User(AbstractBaseUser, PermissionsMixin):
    
    username = models.CharField(max_length=256) # this is never actually used
    
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()
    
    # preferences
    test_items_limit = models.IntegerField(default=5)
    review_interval = models.IntegerField(default=1) # days between search and 1st review


    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.pk)
        
    
    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_personal_words(self):        
        wordlist = PersonalWordlist(self.email)                
        return wordlist
    
    def _remove_personal_word(self, word):
        
        # GET THE EXISTING WORDLIST
        wordlist = PersonalWordlist(self.email)
        wordlist.remove_word(word) 
        
        # RETURN THE UPDATED WORDLIST
        return wordlist



        
class PersonalWordlist(object):
    """
    The personal word list is stored in redis with a key that is
    the user's email address. The corresponding value that redis provides
    is a dictionary of words.    
    """
    
    
    def __init__(self, email):
        self.key = "PW:%s" % email
        self.user = User.objects.get(email=email)
        
        r_server = _get_redis()
        
        # WARNING: uncomment this to completely clear wordlist for testing
        # r_server.delete(self.key)
                
        if r_server.get(self.key):         
            self.words = json.loads(r_server.get(self.key))
        else:
            self.words = {}
            self._update_list(self.words)
                        
    
    def count(self):
        """ Returns the length of the wordlist (ie. how many personal words)"""
        return len(self.words)
        
                                
    def _update_list(self, wordlist):
        """ Take a dictionary of words and update the whole list"""
        
        r_server = _get_redis() 
        r_server.set(self.key, json.dumps(wordlist))
    
    
    def get_items(self, review=False, test=False, timestamp=None):
                
        action = None
        if review:
            action = 'review'
        if test:
            action = 'test'
        
        items = []
        for x,v in self.words.iteritems():
            v['chars'] = x
            
            if action:
                if v['next_action'] != action:
                    continue
                
            if timestamp:
                if v['next_action_date'] > timestamp:
                    continue

            items.append(v)
             
                    
        return items
       
    def _add_word(self, word):
        """ Add a word to the personal wordlist """
        
        wl = self.words
        word = smart_unicode(word)
                
        if word in wl:
            values = wl[word]
            now = datetime.datetime.now()
            gap = time.time() - time.mktime((now - datetime.timedelta(hours=2)).timetuple())
            this_gap = time.time() - values['search_date']
            if this_gap > gap:
                values['last_search'] = time.time() # now
                values['search_count'] += 1
                wl[word] = values
            
        else:
            # we're creating a new word here, so this is the 
            # base for all items in the personal wordlist
            values = {}
            values['created'] = time.time() # now
            values['search_date'] = time.time()  # now
            values['search_count'] = 1
            
            values['view_date'] = time.time()  # now
            values['view_count'] = 1
            
            values['review_date'] = None
            values['review_count'] = 0
            
            values['priority'] = 1 # this is how 'valuable' this word is
            
            # assume this word hasn't been tested and not passed anything
            values['test_date'] = ''
            values['character_pass'] = False
            values['pinyin_pass'] = False
            values['meaning_pass'] = False
            
            # define here what and when the next action should come
            values['next_action'] = 'review'
            one_day_later = datetime.datetime.now() + datetime.timedelta(days=1)
            values['next_action_date'] = time.mktime( ( one_day_later ).timetuple() )
            
            wl[word] = values          
        
                        
        self._update_list(wl)
    
    
    def remove_word(self, word):
        
        wl = self.words
        word = smart_unicode(word)
        
        if word in wl:
            del wl[word]
        
        self._update_list(wl)
        
            
    def _update_word(self, word, view_count=False, reviewed=False, test_results=None):
        
        wordlist = self.words
        word = smart_unicode(word)
        
        if word in wordlist:
        
            # update the number of times the word has been viewed
            if view_count:
                wordlist[word]['view_count'] += 1
            
            
            # update the number of times the word has been reviewed
            if reviewed:
                
                wordlist[word]['review_count'] += 1
                wordlist[word]['review_date'] = time.time()
                wordlist[word]['next_action'] = 'test'
                
                three_days_later = datetime.datetime.now() + datetime.timedelta(days=3)
                wordlist[word]['next_action_date'] = time.mktime( ( three_days_later ).timetuple() )
            
            
            # UPDATE THE WORD BASED ON A TEST THEY JUST COMPLETED
            if test_results:
                
                # get the last test/review date:
                if wordlist[word]['test_date'] == '':
                    last_action_date = wordlist[word]['review_date']
                else:
                    if wordlist[word]['review_date'] > wordlist[word]['test_date']:
                        last_action_date = wordlist[word]['review_date']
                    else:
                        last_action_date = wordlist[word]['test_date']
                
                
                passed = True
                for k,v in test_results.iteritems():
                    wordlist[word][k] = v
                    if v == False:
                        passed = False
                
                if passed:
                    wordlist[word]['next_action'] = 'test'
                    
                    today = (datetime.datetime.fromtimestamp(int(time.time())))
                    last_date = (datetime.datetime.fromtimestamp(int(last_action_date)))
                    new_gap = datetime.timedelta(seconds=(today-last_date).total_seconds() * 2.6)
                    new_date = datetime.datetime.now() + new_gap
                    wordlist[word]['next_action_date'] = time.mktime( ( new_date ).timetuple())
                
                else:
                    wordlist[word]['next_action'] = 'review'
                    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
                    wordlist[word]['next_action_date'] = time.mktime((tomorrow).timetuple())
                
            
            self._update_list(wordlist)
            
        else:
            self.add_word(word)                
                    


# SIGNAL HANDLERS
# -----------------------------------------------
          
def _word_searched(sender, **kwargs):
    """
    This takes a single word from the search function and adds
    it to the user's personal words. This function doesn't split up 
    characters or words, it just accepts whatever comes in, and 
    then adds it to the dictionary.
    """
            
    pwl = PersonalWordlist(kwargs['user_id'])
    pwl._add_word(kwargs['word'])


def _word_viewed(sender, **kwargs):
    """
    Updates a word's view count
    """
    
    pwl = PersonalWordlist(kwargs['user_id'])
    pwl._update_word(kwargs['word'], view_count=True)
    
# CONNECT SOME SIGNALS TO SOME FUNCTIONS
word_searched.connect(_word_searched, dispatch_uid=uuid.uuid4().hex)
word_viewed.connect(_word_viewed, dispatch_uid=uuid.uuid4().hex)

