from django.conf import settings
from website.models import *
from django_mobile import get_flavour

import ast

def common(request):
    import settings
    context = {}
    context['ga_is_on'] = settings.GA_IS_ON
    context['siteurl'] = settings.SITE_URL
    context['sitename'] = settings.SITE_NAME
    context['base_template'] = settings.BASE_TEMPLATE
    if get_flavour(request) == 'mobile':
        context['base_template'] = settings.BASE_TEMPLATE_MOBILE
    
    show_sidebar = False
    if 'show_sidebar' in request.session:
        show_sidebar = ast.literal_eval(request.session['show_sidebar'])
    
    context['show_sidebar'] = show_sidebar
    
    

    return context
    
