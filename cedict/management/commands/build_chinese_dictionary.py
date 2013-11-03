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
        # 一事無成 一事无成 [yi1 shi4 wu2 cheng2] /to have achieved nothing/to be a total failure/to get nowhere/

        file = open(settings.DICT_FILE_LOCATION)
        r_server = _get_redis()
        
        # EMPTY ALL ZH KEYS
        item_count = 0
        keys = r_server.keys('ZH:*')
        for x in keys:
            r_server.delete(x)
            item_count += 1
        print "Deleted %s Chinese characters" % item_count
        
        
        # EMPTY ALL PY KEYS
        item_count = 0
        keys = r_server.keys('PY:*')
        for x in keys:
            r_server.delete(x)
            item_count += 1
        print "Deleted %s Pinyin entries" % item_count
        
        
        
        # NOW LETS START
        item_count = 0
        for line in file:
            if line.startswith("#"):
                pass
            else:
                
                # GATHER ALL THE MAIN VARIABLES
                new = line.split()
                numbered_pinyin = line[(line.index('[')+1):(line.index(']'))]
                f = ReadingFactory()
                tonal_pinyin =  f.convert(numbered_pinyin, 'Pinyin', 'Pinyin',
                    sourceOptions={'toneMarkType': 'numbers', 'yVowel': 'v',
                    'missingToneMark': 'fifth'})
                meanings = line[(line.index('/')+1):(line.rindex('/'))]               
                pinyin_key = "PY:%s" % numbered_pinyin.replace(' ', '_')
                character_key = "ZH:%sC:%s" % ((len((new[1]))/3), new[1]) 
                
                
                # ADD THE PINYIN ENTRY
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
    
    
                # ADD THE CHARACTER ENTRY
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
        
        print "%s Chinese items added" % item_count          
        file.close()        


"""


 
"""