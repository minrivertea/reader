from django.conf import settings
from website.models import *

def common(request):
    import settings
    context = {}
    context['ga_is_on'] = settings.GA_IS_ON
    context['siteurl'] = settings.SITE_URL
    context['sitename'] = settings.SITE_NAME
    return context
    
