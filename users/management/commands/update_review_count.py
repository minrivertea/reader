#!/usr/bin/python
# -*- coding: utf8 -*-


# django
from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta


# python
import uuid
import time

# apps
from utils.redis_helper import _get_redis, _search_redis
from users.models import User, PersonalWordlist


# this sends out the first 'review' email after the order was shipped.
class Command(NoArgsCommand):
    """ 
    This collects up all of the users who need reminders about their personal
    words, and sends them an appropriate email reminder with a link.   
    """
    
    help = 'Temp to update review count of users words'
    

    def handle_noargs(self, **options):
                
        for u in User.objects.all():
            
            # GET PERSONAL WORDLIST
            items = u.get_personal_words().get_items()
            review_count = 0
            re_review_count = 0
            
            
            for x in items:
                review_count += int(x['review_count'])
                if int(x['review_count']) > 0:
                    re_review_count += ( int(x['review_count']) - 1 )

            u.words_reviewed += review_count
            u.words_reviewed_again += re_review_count
                        
            
            
            
            u.save()
                        
            
           
                
                
                
                
                
                
                
                
                
                
