from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import views
from cedict.views import get_examples, get_similar, copy_dictionary, single_word

urlpatterns = patterns('',
    
    url(r'^$', views.home, name="home"),
    url(r'^articles/$', views.articles, name="articles"),
    url(r'^get-examples/(?P<word>[\w-]+)/$', get_examples, name="get_examples"),
    url(r'^get-similar/(?P<word>[\w-]+)/$', get_similar, name="get_similar"),
    url(r'^search/$', views.search, name="search"),
    url(r'^search/(?P<search_string>[\w-]+)/$', views.search, name="search"),
    url(r'^copy_dict/$', copy_dictionary, name="copy_dictionary"),
    url(r'^vocab/$', views.vocab, name="vocab"),
    url(r'^vocab/(?P<word>[\w-]+)/$', single_word, name="single_word"),
    url(r'^stats/$', views.stats, name="stats"),
    url(r'^get-personal-words/$', views.get_personal_words, name="get_personal_words"),
)