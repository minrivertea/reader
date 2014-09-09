#!/usr/bin/python
# -*- coding: utf8 -*-

from django.conf import settings

from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

import uuid
import json
import re
from django.utils.encoding import smart_str, smart_unicode
from django.core import serializers



# import various bits and pieces
from utils.redis_helper import _get_redis, _search_redis, _add_to_redis
from cedict.words import ChineseWord

from cjklib import characterlookup
from cjklib.dictionary import *
from cjklib.reading import ReadingFactory


# this sends out the first 'review' email after the order was shipped.
class Command(NoArgsCommand):
        
    help = 'Adds additional information to each of the Chinese dictionary entries'

   
    def handle_noargs(self, **options):
        # 一事無成 一事无成 [yi1 shi4 wu2 cheng2] /to have achieved nothing/to be a total failure/to get nowhere/
        
        r_server = _get_redis()
        
        # get all the character entries in the dict (100k roughly)
        key = "ZH:1C:*"
        all_keys = r_server.scan_iter(key)
        
        # go through each key, find out what words start with this one
        loop = 0
        for key in all_keys:
            
            this_word = ChineseWord(chars=smart_unicode(key.split(':')[2]))
            
            starts_with = []
            for y in this_word._starts_with():
                starts_with.append(y.chars)

            
            contains = []
            for y in this_word._contains():
                contains.append(y.chars)
                
            
            # SAVE THE VALUES
            this_word.starts_with = starts_with
            this_word.contains = contains
            values = vars(this_word) # nice, serialises the object values
            r_server.set(key, json.dumps(values))

            
            loop += 1
            print loop
            
                     


"""


 
"""