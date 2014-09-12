#!/usr/bin/python
# -*- coding: utf8 -*-

# Django settings for reader project.
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS

import os
PROJECT_PATH = os.path.normpath(os.path.dirname(__file__))


DEBUG =                 False
TEMPLATE_DEBUG =        DEBUG
GA_IS_ON =              False
ADMINS =                (('Chris', 'info@chinesedictionary.io'),)
MANAGERS =              ADMINS
ALLOWED_HOSTS =         ['www.chinesedictionary.io', 'chinesedictionary.io', 'reader.westiseast.co.uk']                                   


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

TIME_ZONE =             'America/Chicago'
LANGUAGE_CODE =         'en-gb'
SITE_ID =               1
USE_I18N =              False
USE_L10N =              False
SECRET_KEY =            ''


# STATIC FILES
# ------------------------------------------------------

MEDIA_ROOT =                os.path.join(PROJECT_PATH, 'media')
MEDIA_URL =                 '/media/'
STATIC_URL =                '/static/'
STATIC_ROOT =               os.path.join(PROJECT_PATH, 'static')
ADMIN_MEDIA_PREFIX =        '/media/'
STATICFILES_DIRS =          ()
STATICFILES_FINDERS =       ('django.contrib.staticfiles.finders.FileSystemFinder',
                            'django.contrib.staticfiles.finders.AppDirectoriesFinder',
                            'compressor.finders.CompressorFinder',)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django_mobile.middleware.MobileDetectionMiddleware',
    'django_mobile.middleware.SetFlavourMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'reader.urls'



# TEMPLATING
# ------------------------------------------------------

TEMPLATE_LOADERS = (
    'django_mobile.loader.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS += (
     'django.core.context_processors.request',
     'django.contrib.messages.context_processors.messages',
     'context_processors.common',
     'django_mobile.context_processors.flavour',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, "templates/")
)

BASE_TEMPLATE = 'base.html'
BASE_TEMPLATE_MOBILE = 'base_responsive.html'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    # 'debug_toolbar',
    'registration',
    'website',
    'users',
    'cedict',
    'srs',
    'south',
    'django_mobile',
    'compressor',
    'nginx_memcache', # do we need this?
)





# RANDOM STUFF
# ------------------------------------------------------

SITE_URL = 'http://chinesedictionary.io'
SITE_NAME = 'chinesedictionary.io'
ACCOUNT_ACTIVATION_DAYS = 7
DICT_FILE_LOCATION = os.path.join(PROJECT_PATH, 'files/cedict_1_0_ts_utf-8_mdbg.txt')
ENGLISH_WORD_LIST = os.path.join(PROJECT_PATH, 'files/en_wordlist.txt')
CHINESE_DICTIONARY_DUMP_FILENAME = os.path.join(PROJECT_PATH, 'dumps/chinese_dictionary.txt.gz')


# CACHE SETTINGS
# ------------------------------------------------------

CACHE_NGINX = True
CACHE_NGINX_TIME = 3600 * 24  # 1 day, in seconds
CACHE_NGINX_ALIAS = 'default'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# ACCOUNTS AND USERS STUFF
# ------------------------------------------------------

ACCOUNT_ACTIVATION_DAYS = 7
AUTHENTICATION_BACKENDS = (
    'users.custom_authentication_backend.CustomAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = '/user/'
LOGIN_URL = 'auth_login' # this is a named URL not an actual URL



# KEYS FOR REDIS SEARCHING
# ------------------------------------------------------

CHINESE_WORD_KEY = "ZH:%sC:%s" # eg. ZH:2C:好吧 (the middle '2C' means how many characters)
PINYIN_WORD_KEY = "PY:%s" # eg. PY:buhao
ENGLISH_WORD_KEY = "EN:%sW:%s"
MEASURE_WORD_KEY = "MW:%s" # eg. MW:个



# RANDOM SETTINGS FOR THE SRS
# ------------------------------------------------------

DEFAULT_REVIEW_TEST_INTERVAL = 3 # days



# EMAILS
# ------------------------------------------------------
EMAIL_BASE_HTML_TEMPLATE = ''
SERVER_EMAIL = 'info@chinesedictionary.io' #important for sending error notifications 
SITE_EMAIL = 'ChineseDictionary.io <info@chinesedictionary.io>'
DEFAULT_FROM_EMAIL = SITE_EMAIL
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
SEND_BROKEN_LINK_EMAILS = False 

try:
    from local_settings import *
except ImportError:
    pass
    




