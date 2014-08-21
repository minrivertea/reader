from django.conf.urls.defaults import *
import views
from cedict.views import single_word

urlpatterns = patterns('',
    
    # BASE URLS
    url(r'^$', views.home, name="home"),
    
    # SEARCH URLS
    url(r'^search/(?P<word>[\w-]+)/startswith/$', views.search_starts_with, name="search_starts_with"),
    url(r'^search/(?P<word>[\w-]+)/contains/$', views.search_contains, name="search_contains"),
    url(r'^search/(?P<search_string>[\w-]+)/$', views.search, name="search_with_string"),
    url(r'^search/$', views.search, name="search"),
        
    
    # DICTIONARY URLS
    url(r'^words/(?P<chars>[\w-]+)/$', single_word, name="single_word"),
        
    
)