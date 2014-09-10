#!/usr/bin/python
# -*- coding: utf8 -*-


# django
from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta
from django.template import RequestContext, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.urlresolvers import reverse


# python
import uuid
import time

# apps
from utils.redis_helper import _get_redis, _search_redis
from utils.helpers import _send_email
from users.models import User, PersonalWordlist


# this sends out the first 'review' email after the order was shipped.
class Command(NoArgsCommand):
    """ 
    This collects up all of the users who need reminders about their personal
    words, and sends them an appropriate email reminder with a link.   
    """
    
    help = 'Sends reminder emails to users with personal wordlists'
    

    def handle_noargs(self, **options):
                
        for u in User.objects.all():
            
            
            # GET REVIEW ITEMS
            review_url = False
            review_items = PersonalWordlist(u.email).get_items(review=True, timestamp=time.time())
            if len(review_items) > 0:
                review_url = reverse('review_new')
            
            # GET TEST ITEMS
            test_url = False
            test_items = PersonalWordlist(u.email).get_items(test=True, timestamp=time.time())
            if len(test_items) > 0: 
                test_url = reverse('test')
            
            
            # IF THERE'S ANYTHING, CREATE AN EMAIL
            if review_url or test_url:
                
                _send_email(
                    recipient = u.email,
                    subject_line = "It's time to review your vocab!",
                    template = 'srs/emails/notification.txt',
                    extra_context = {
                        'review_url': review_url,
                        'test_url': test_url,   
                    }
                )
                
                
                
                
                
                
                
                
                
                
                
                
                
                
