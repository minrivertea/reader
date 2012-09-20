from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import views

urlpatterns = patterns('',
    url(r'^$', views.home, name="home"),
    url(r'^about/$', views.about, name="about"),
    url(r'^text/(?P<hashkey>[\w-]+)/$', views.text, name="text"),
    url(r'^url/(?P<hashkey>[\w-]+)/$', views.url, name="url"),
    url(r'^copy_dict/$', views.copy_dictionary, name="copy_dictionary"),
)