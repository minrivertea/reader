#!/usr/bin/python
# -*- coding: utf8 -*-

from django.conf import settings

from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

import uuid


# import various bits and pieces
from utils.redis_helper import _get_redis, _search_redis, _add_to_redis

from cjklib import characterlookup
from cjklib.dictionary import *
from cjklib.reading import ReadingFactory


# this sends out the first 'review' email after the order was shipped.
class Command(NoArgsCommand):
    help = 'Rebuilds from scratch the Chinese-English Dictionary'

    def handle_noargs(self, **options):
         # eg 一中一台 [yi1 Zhong1 yi1 Tai2] /first meaning/second meaning/
        file = open(settings.DICT_FILE_LOCATION)
        r_server = _get_redis()
        
        for line in file:
            if line.startswith("#"):
                pass
            else:
                new = line.split()
    
                numbered_pinyin = line[(line.index('[')+1):(line.index(']'))]
                f = ReadingFactory()            
                pinyin =  f.convert(numbered_pinyin, 'Pinyin', 'Pinyin',
                    sourceOptions={'toneMarkType': 'numbers', 'yVowel': 'v',
                    'missingToneMark': 'fifth'})
                
                meanings = line[(line.index('/')+1):(line.rindex('/'))]
    
                key = "%sC:%s" % ((len((new[1]))/3), new[1])                
    
                if r_server.exists(key):
                    object = _search_redis(key)
                    print object
                    try:
                        val = "meaning%s" % (int(object['count']) + 1)
                        object[val]
                    except KeyError:
                        
                        count = (int(object['count']) + 1)
                        new1 = "meaning%s" % count
                        new2 = "pinyin%s" % count
                        
                        mapping = {
                            new1: meanings,
                            new2: pinyin, 
                            'count': count,
                        }
                        
                        r_server.hmset(key, mapping)
                            
                else:
                    mapping = {
                        'chars': new[1],
                        'pinyin1': pinyin, 
                        'meaning1': meanings,
                        'count': 1,
                        'id': uuid.uuid4().hex,
                    }
                    
                    r_server.hmset(key, mapping)
                    
        file.close()        


"""


 
"""