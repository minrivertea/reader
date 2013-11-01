# Django settings for reader project.
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS


import os
PROJECT_PATH = os.path.normpath(os.path.dirname(__file__))


DEBUG = False
TEMPLATE_DEBUG = DEBUG
GA_IS_ON = False

ADMINS = (
    ('Chris', 'chris@minrivertea.com'),
)

MANAGERS = ADMINS

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

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
USE_I18N = False
USE_L10N = False


MEDIA_ROOT = os.path.join(PROJECT_PATH, 'static')
MEDIA_URL = '/'
ADMIN_MEDIA_PREFIX = '/media/'



# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)


TEMPLATE_CONTEXT_PROCESSORS += (
     'django.core.context_processors.request',
     'context_processors.common',
)

ROOT_URLCONF = 'reader.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, "templates/")
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'website',
    'django.contrib.admin',
    'django_static',
    #'debug_toolbar',
    'endless_pagination',
    'registration',
    'cedict',
)

#ENDLESS PAGINATION SETTINGS:
ENDLESS_PAGINATION_PER_PAGE = 200
ENDLESS_PAGINATION_LOADING = '<img src="/images/loading.gif" />'

# django-static info
DJANGO_STATIC = True
DJANGO_STATIC_SAVE_PREFIX = '/tmp/cache-forever'
DJANGO_STATIC_NAME_PREFIX = '/cache-forever'
#DJANGO_STATIC_MEDIA_URL = '//static.kandongle.me'


#random stuff
SITE_URL = 'http://chinesedictionary.io'
SITE_NAME = 'chinesedictionary.io'
ACCOUNT_ACTIVATION_DAYS = 7
AUTH_PROFILE_MODULE = "website.Account"
DICT_FILE_LOCATION = os.path.join(PROJECT_PATH, 'files/cedict_1_0_ts_utf-8_mdbg.txt')
ENGLISH_WORD_LIST = os.path.join(PROJECT_PATH, 'files/en_wordlist.txt')



# EMAILS
SERVER_EMAIL = 'info@chinesedictionary.io' #important for sending error notifications 
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
SEND_BROKEN_LINK_EMAILS = False 

try:
    from local_settings import *
except ImportError:
    pass
    
LOG_FILENAME = ""

import logging 
                    
logging.basicConfig(filename=LOG_FILENAME,
                   level=logging.DEBUG,
                   datefmt="%Y-%m-%d %H:%M:%S",
                   format="%(asctime)s %(levelname)s %(name)s %(message)s",
                  )

