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
    
    
    # NOTIFICATIONS
    if request.user.is_authenticated():
    
        test_items = request.session.get('TEST_NOTIFICATIONS', len(request.user.get_test_items()))
        review_items = request.session.get('TEST_NOTIFICATIONS', len(request.user.get_review_items()))
    
        context['review_notifications'] = review_items
        context['test_notifications'] = test_items
        context['total_notifications'] = test_items + review_items
        
    

    return context
    
