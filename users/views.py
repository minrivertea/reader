#!/usr/bin/python
# -*- coding: utf8 -*-

import string, unicodedata
import redis
import os
PROJECT_PATH = os.path.normpath(os.path.dirname(__file__))

from urlparse import urlparse

import uuid
import random
import re
import urllib2
import datetime
import time

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils import simplejson
from django.template.loader import render_to_string
from django.utils.encoding import smart_str, smart_unicode
from django.utils.http import is_safe_url
from django.shortcuts import resolve_url

from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from forms import CustomAuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME


from utils.helpers import _render, _is_english, _is_punctuation, _is_number, _split_unicode_chrs, _get_crumbs, _update_crumbs
from utils.redis_helper import _get_redis, _search_redis, _add_to_redis, _increment_stats
import utils.messages as messages

from srs.views import _collect_vocab


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=CustomAuthenticationForm,
          current_app=None, extra_context=None):

        
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():
            
            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            from django.contrib.auth import login
            login(request, form.get_user())

            return HttpResponseRedirect(redirect_to)

    else:
        form = authentication_form(request)


    context = {
        'form': form,
        redirect_field_name: redirect_to,
    }
    if extra_context is not None:
        context.update(extra_context)
    return _render(request, template_name, context)
    


def user(request):
    user = request.user
    return _render(request, 'users/user.html', locals())



def remove_personal_word(request, word):
    
    user = request.user
    user._remove_personal_word(word)
    
    if request.is_ajax():
        
        return HttpResponse('OK')
        
    url = request.META.get('HTTP_REFERER','/')
    return HttpResponseRedirect(url)

def update_user_preferences(request):
    
    # get the parameters from the URL and then convert to session prefs etc.
    for x,v in request.GET.items():
        
        request.session[x] = v
    
    if request.is_ajax():
        return HttpResponse('OK')
    
    url = request.META.get('HTTP_REFERER','/')
    return HttpResponseRedirect(url)
