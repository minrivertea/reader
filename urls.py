from django.conf.urls.defaults import *
from django.conf import settings
from django.conf.urls.static import static

from website.views import page

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('website.urls')),
    (r'^reader/', include('creader.urls')),
    (r'^user/', include('users.urls')),

    (r'^admin/', include(admin.site.urls)),
    url(r'^(?P<slug>[\w-]+)/$', page, name="page"),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)