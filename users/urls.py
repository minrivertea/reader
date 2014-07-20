from django.conf.urls.defaults import *
from django.conf import settings
import django.views.static
from django.core.urlresolvers import reverse_lazy

from views import *
from custom_registration_backend import CustomRegistrationView
from django.contrib.auth import views as auth_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', user, name="user"),
    
    # django-registration urls
    url(r'^register/$', CustomRegistrationView.as_view(), name='registration_register'),
    url(r'^login/$', login, name='auth_login'),
    url(r'^password/change/$',
                           auth_views.password_change,
                           {'post_change_redirect': reverse_lazy('auth_password_change_done')},
                           name='auth_password_change'),
    url(r'^password/change/done/$',
                           auth_views.password_change_done,
                           name='auth_password_change_done'),
    url(r'^password/reset/$',
                           auth_views.password_reset,
                           {'post_reset_redirect': reverse_lazy('auth_password_reset_done')},
                           name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
                           auth_views.password_reset_confirm,
                           name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$',
                           auth_views.password_reset_complete,
                           name='auth_password_reset_complete'),
    url(r'^password/reset/done/$',
                           auth_views.password_reset_done,
                           name='auth_password_reset_done'),
    
    (r'^', include('registration.backends.default.urls')),
   
   
    url(r'^remove_personal_word/(?P<word>[\w-]+)$', remove_personal_word, name="remove_personal_word"),
    url(r'^update_prefs/$', update_user_preferences, name='update_user_preferences'),
)

