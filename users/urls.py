from django.conf.urls.defaults import *
from django.conf import settings
import django.views.static

from registration.views import register

from users.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', user, name="user"),
    url(r'^vocab/(?P<chars>[\w-]+)/$', user_vocab_item, name="user_vocab_item"),
    url(r'^vocab/$', user_vocab, name="user_vocab"),
    url(r'^articles/$', user_articles, name="user_articles"),
)

