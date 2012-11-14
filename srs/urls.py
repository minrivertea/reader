from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    
    url(r'^$', views.home, name="home"),
#    url(r'^articles/$', views.articles, name="articles"),
#    url(r'^get-examples/(?P<word>[\w-]+)/$', views.get_examples, name="get_examples"),

)