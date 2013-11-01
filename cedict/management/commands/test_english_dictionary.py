#!/usr/bin/python
# -*- coding: utf8 -*-

from django.conf import settings

from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

import uuid
import string

# import various bits and pieces
from utils.redis_helper import _get_redis, _search_redis, _add_to_redis

from cjklib import characterlookup
from cjklib.dictionary import *
from cjklib.reading import ReadingFactory



# this sends out the first 'review' email after the order was shipped.
class Command(NoArgsCommand):
    help = 'Test how many words from a standard EN wordlist get matches in the Dictionary'

    def handle_noargs(self, **options):
        file = open(settings.ENGLISH_WORD_LIST)
        r_server = _get_redis()
        
        # NOW LETS START
        item_count = 0
        for line in file:
            key = "EN:1W:%s" % line.strip()
            if r_server.exists(key):
                print "got a match: %s" % line
                item_count += 1
            
            
            if item_count == 100:
                break
                
        
        print "Got back %s matches from the dictionary" % item_count          
        file.close()        

"""


 
"""