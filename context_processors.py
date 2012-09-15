from django.conf import settings
from website.models import *

def common(request):
    import settings
    context = {}
    context['ga_is_on'] = settings.GA_IS_ON
    return context
    
