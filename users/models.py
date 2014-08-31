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

from datetime import datetime, timedelta
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
    
    # test related stats tracking
    no_answered = models.IntegerField(default=0, blank=True, null=True)
    no_correct = models.IntegerField(default=0, blank=True, null=True)
    no_wrong = models.IntegerField(default=0, blank=True, null=True)
    

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.pk)
    
    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name    
    
    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_personal_words(self):        
        wordlist = PersonalWordlist(self.email)                
        return wordlist
    
    def get_test_items(self):
        return self.get_personal_words().get_items(test=True, timestamp=time.time())
    
    def get_review_items(self):
        return self.get_personal_words().get_items(review=True, timestamp=time.time())
    
    def get_success_percent(self):
        if self.no_correct and self.no_answered:
            return ( ( self.no_correct / self.no_answered) * 100 )
        return None
    
    def _remove_personal_word(self, word):
        
        # GET THE EXISTING WORDLIST
        wordlist = PersonalWordlist(self.email)
        wordlist.remove_word(word) 
        
        # RETURN THE UPDATED WORDLIST
        return wordlist
    
    def _increment_stats(self, add=None, minus=None):
        "Increment the test stats for the user"
        if add:
            self.no_correct += 1
        if minus:
            self.no_wrong += 1
        self.no_answered += 1
        



        
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
    
    
    def get_items(self, review=False, test=False, timestamp=None, action=None):
                
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
            now = datetime.now()
            gap = time.time() - time.mktime((now - timedelta(hours=2)).timetuple())
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
                        
            # assume this word hasn't been tested and not passed anything
            values['test_date'] = ''
            values['test_count'] = 0
            values['test_pass'] = 0
            
            values['character_pass'] = False
            values['character_pass_count'] = 0
            values['pinyin_pass'] = False
            values['pinyin_pass_count'] = 0
            values['meaning_pass'] = False
            values['meaning_pass_count'] = 0
            
            # define here what and when the next action should come
            values['next_action'] = 'review'
            one_day_later = datetime.now() + timedelta(days=1)
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
            
            
            # UPDATE REVIEWED INFORMATION
            if reviewed:
                
                wordlist[word]['review_count'] += 1
                wordlist[word]['review_date'] = time.time()
                wordlist[word]['next_action'] = 'test'
                three_days_later = datetime.now() + timedelta(days=3)                
                wordlist[word]['next_action_date'] = time.mktime(( three_days_later ).timetuple())
                            
                                        
            # UPDATE THE WORD BASED ON A TEST THEY JUST COMPLETED
            if test_results:
                
                now = time.time()
                
                # get the last test/review date:
                if wordlist[word]['test_date'] == '': 
                    lad = wordlist[word]['review_date'] # last_action_date
                else:
                    if wordlist[word]['review_date'] > wordlist[word]['test_date']:
                        lad = wordlist[word]['review_date']
                    else:
                        lad = wordlist[word]['test_date']
                
                passed = True
                wordlist[word]['test_date'] = time.time()
                
                for k,v in test_results.iteritems():
                    print "%s:  %s" % (k, v)
                    wordlist[word][k] = v
                    try:
                        wordlist[word][('%s_count' % k)] = int(wordlist[word][('%s_count' % k)]) + 1
                    except:
                        wordlist[word][('%s_count' % k)] = 1
                    
                    if v == False:
                        passed = False
                    
                
                    
                if passed == False:
                    
                    # test failed, setup a review
                    tomorrow = datetime.now() + timedelta(days=1)
                    wordlist[word]['next_action'] = 'review'
                    wordlist[word]['next_action_date'] = time.mktime((tomorrow).timetuple())
                    
                else:                
                    print "updating test date"
                    print "NOW: %s" % datetime.fromtimestamp(float(lad))
                    # test passed, setup a new test at a later date
                    ld = (datetime.fromtimestamp(float(lad))) # last date
                    ti = timedelta(seconds=(datetime.now()-ld).total_seconds()) # this interval
                    if ti < timedelta(days=1):
                        ti = timedelta(days=1)
                    ni = ti.total_seconds() * 2.6
                    nd = datetime.now() + timedelta(seconds=ni)

                    wordlist[word]['next_action'] = 'test'
                    wordlist[word]['next_action_date'] = time.mktime( ( nd ).timetuple())
                    
                    print "NEXT: %s" % nd
                                        
                                                
            # self._update_list(wordlist)
            
        else:
            self._add_word(word)                
                    


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

