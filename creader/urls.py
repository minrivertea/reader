from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',    
    url(r'^$', views.url, name="url"),
    url(r'^(?P<hashkey>[\w-]+)/$', views.text, name="text"),
)