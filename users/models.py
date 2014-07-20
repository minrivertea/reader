#-*- coding: utf-8 -*-

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
import ast
from urlparse import urlparse

from django.core.signals import request_finished
from django.utils.encoding import smart_str, smart_unicode

from website.signals import word_searched, article_saved
from creader.views import _group_words 
from utils.redis_helper import _search_redis, _get_redis
from utils.helpers import _split_unicode_chrs



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

    # define here other needed methods
    def get_personal_words(self):
                
        key = "PW:%s" % self.email
        wordlist = ast.literal_eval(_search_redis(key)['wordlist'])
        
        return wordlist
    
    def _remove_personal_word(self, word):
        
        # GET THE EXISTING WORDLIST
        key = "PW:%s" % self.email
        wordlist = ast.literal_eval(_search_redis(key)['wordlist'])
        
        to_delete = []
        for x in wordlist:
            if word == smart_unicode(x):
                to_delete.append(x)
        
        for x in to_delete:
            del wordlist[x]
                
        # UPDATE REDIS
        r_server = _get_redis()
        mapping = {
            'wordlist': wordlist,
        }
        r_server.hmset(key, mapping) 
        
        # RETURN THE UPDATED WORDLIST
        return wordlist
        
        
    
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
        



# SIGNAL HANDLERS
# -----------------------------------------------

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
    
           


# SAVES A SEARCHED WORD TO THE USER'S PERSONAL WORD LIST
def save_word(sender, **kwargs):
    """
    This takes a single word from the search function and adds
    it to the user's personal words. This function doesn't split up 
    characters or words, it just accepts whatever comes in, and 
    then adds it to the dictionary.
    """
        
    word = kwargs['word']['chars']


    # PREPARE CONNECTION AND THE USER'S KEY              
    r_server = _get_redis()
    key = "PW:%s" % kwargs['user_id']    
    
    # RETRIEVE THE WORDLIST FROM REDIS OR CREATE A NEW ONE
    if r_server.exists(key):        
        wordlist = ast.literal_eval(_search_redis(key)['wordlist'])
    else:
        wordlist = {}    
    
            
    # DECIDE IF THE WORD IS NEW OR NOT
    if word in wordlist:
        
        # ONLY UPDATE VALUES IF THE LAST_SEARCHED TIME AND CURRENT TIME ARE GREATER THAN 2 HOURS
        now = datetime.datetime.now()
        two_hour_gap = time.time() - time.mktime((now - datetime.timedelta(hours=2)).timetuple())
        this_gap = time.time() - wordlist[word]['last_searched']
        
        if this_gap > two_hour_gap:
            wordlist[word]['last_searched'] = time.time()
            wordlist[word]['searched_count'] += 1
        else:
            pass
                
    else:
        # ADD IT TO THE LIST IF IT'S NEW
        vals = {}
        vals['created'] = time.time() # now
        vals['last_searched'] = time.time() # now
        vals['searched_count'] = 1
        wordlist[word] = vals       
    
    mapping = {
        'wordlist': wordlist,
    }
                    
    r_server.hmset(key, mapping)        

word_searched.connect(save_word)

