from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    
    url(r'^$', views.test_home, name="test_home"),
    url(r'^review/$', views.review_new, name="review_new"),
    url(r'^test/$', views.test, name="test"),
    url(r'^test/submit_answer$', views.submit_answer, name="submit_answer"),
#    url(r'^articles/$', views.articles, name="articles"),
#    url(r'^get-examples/(?P<word>[\w-]+)/$', views.get_examples, name="get_examples"),

)