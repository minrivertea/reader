#!/usr/bin/python
# -*- coding: utf8 -*-

from django.conf import settings

from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

import uuid


# import various bits and pieces
from utils.redis_helper import _get_redis, _search_redis, _add_to_redis
from utils.helpers import _convert_pinyin_to_numbered_notation

from cjklib import characterlookup
from cjklib.dictionary import *
from cjklib.reading import ReadingFactory


# this sends out the first 'review' email after the order was shipped.
class Command(NoArgsCommand):
    help = 'Rebuilds from scratch the Chinese-English Dictionary'

    def handle_noargs(self, **options):
        # EXAMPLE: 一中一台 [yi1 Zhong1 yi1 Tai2] /first meaning/second meaning/
        file = open(settings.DICT_FILE_LOCATION)
        r_server = _get_redis()
        
        # EMPTY THE WHOLE DATABASE NOW
        r_server.flushdb()
        
        # NOW LETS START
        item_count = 0
        for line in file:
            if line.startswith("#"):
                pass
            else:
                new = line.split()
    
                numbered_pinyin = line[(line.index('[')+1):(line.index(']'))]
                
                f = ReadingFactory()            
                tonal_pinyin =  f.convert(numbered_pinyin, 'Pinyin', 'Pinyin',
                    sourceOptions={'toneMarkType': 'numbers', 'yVowel': 'v',
                    'missingToneMark': 'fifth'})
                
                meanings = line[(line.index('/')+1):(line.rindex('/'))]
    
                # ADD A KEY WITH THE PINYIN NOW                
                pinyin_key = "PINYIN:%s" % numbered_pinyin.replace(' ', '_')
                character_key = "%sC:%s" % ((len((new[1]))/3), new[1]) 
                
                # NOW CHECK AND ADD A PINYIN KEY TO REDIS
                if r_server.exists(pinyin_key):
                    object = _search_redis(pinyin_key)
                    mapping = {
                        'character_keys': "".join( (object['character_keys'], ',', character_key) ),   
                    }
                    r_server.hmset(pinyin_key, mapping)
                                        
                else:
                    mapping = {
                        'character_keys': character_key,
                        'id': uuid.uuid4().hex,
                    }
                    r_server.hmset(pinyin_key, mapping)                    
    
    
                # NOW MOVE ON TO THE CHARACTER
                if r_server.exists(character_key):
                     
                    object = _search_redis(character_key)
                    try:
                        val = "meaning%s" % (int(object['count']) + 1)
                        object[val]
                    except KeyError:
                        
                        count = (int(object['count']) + 1)
                        new1 = "meaning%s" % count
                        new2 = "pinyin%s" % count
                        
                        mapping = {
                            new1: meanings,
                            new2: tonal_pinyin, 
                            'count': count,
                        }
                        
                        r_server.hmset(character_key, mapping)
                            
                else:
                    mapping = {
                        'chars': new[1],
                        'pinyin1': tonal_pinyin, 
                        'meaning1': meanings,
                        'count': 1,
                        'id': uuid.uuid4().hex,
                    }
                    
                    r_server.hmset(character_key, mapping)
                
                item_count += 1
        
        print "%s dictionary items added" % item_count          
        file.close()        


"""


 
"""