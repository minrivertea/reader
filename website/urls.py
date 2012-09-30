from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import views

urlpatterns = patterns('',
    url(r'^$', views.home, name="home"),
    url(r'^search/$', views.home, name="search"),
    url(r'^search/(?P<word>[\w-]+)/$', views.single_word, name="search_word"),
    url(r'^copy_dict/$', views.copy_dictionary, name="copy_dictionary"),
    url(r'^vocab/$', views.vocab, name="vocab"),
    url(r'^vocab/(?P<word>[\w-]+)/$', views.single_word, name="single_word"),
    url(r'^stats/$', views.stats, name="stats"),
    url(r'^get-personal-words/$', views.get_personal_words, name="get_personal_words"),
    url(r'^text/(?P<hashkey>[\w-]+)/$', views.text, name="text"),
    url(r'^url/(?P<hashkey>[\w-]+)/$', views.url, name="url"),
    url(r'^(?P<slug>[\w-]+)/$', views.page, name="page"),
)