from django.conf.urls.defaults import *
import views
from cedict.views import single_word

urlpatterns = patterns('',
    
    # BASE URLS
    url(r'^$', views.home, name="home"),
    url(r'^articles/$', views.articles, name="articles"),
    
    # SEARCH URLS
    url(r'^search/(?P<search_string>[\w-]+)/bw/$', views.search_beginning_with, name="search_beginning_with"),
    url(r'^search/(?P<search_string>[\w-]+)/contains/$', views.search_contains, name="search_contains"),
    url(r'^search/(?P<search_string>[\w-]+)/$', views.search, name="search_with_string"),
    url(r'^search/$', views.search, name="search"),
    
    url(r'^get-personal-words/$', views.get_personal_words, name="get_personal_words"),
    
    
    # DICTIONARY URLS
    url(r'^words/$', views.words, name="words"),
    url(r'^words/(?P<word>[\w-]+)/$', single_word, name="single_word"),
    
    # UTILS URLS
    url(r'^stats/$', views.stats, name="stats"),
    
    
)