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
    help = 'Builds the Chinese-English Dictionary.'

    

    def _del_keys(self, key):
        r_server = _get_redis()
        keys = r_server.keys(key)
        item_count = 0
        for x in keys:
            r_server.delete(x)
            item_count += 1
        
        print "Deleted %s items matching %s" % (item_count, key)
        return

    def handle_noargs(self, **options):
        # 一事無成 一事无成 [yi1 shi4 wu2 cheng2] /to have achieved nothing/to be a total failure/to get nowhere/

        # EMPTY ALL ZH + PY KEYS
        self._del_keys('ZH:*')
        self._del_keys('PY:*')
        
        # NOW LETS START
        file = open(settings.DICT_FILE_LOCATION)
        item_count = 0
        for line in file:
            if line.startswith("#"):
                pass
            else:
                
                # GATHER ALL THE MAIN VARIABLES
                new = line.split()
                num_pinyin = line[(line.index('[')+1):(line.index(']'))]
                f = ReadingFactory()
                tonal_pinyin =  f.convert(num_pinyin, 'Pinyin', 'Pinyin',
                    sourceOptions={'toneMarkType': 'numbers', 'yVowel': 'v',
                    'missingToneMark': 'fifth'})
                meanings = line[(line.index('/')+1):(line.rindex('/'))]               
                py_key = "PY:%sW:%s" % (len(num_pinyin.split(' ')), num_pinyin.replace(' ', '_'))
                char_key = "ZH:%sC:%s" % ((len((new[1]))/3), new[1]) 
                
                
                # ADD THE PINYIN ENTRY
                
                r_server = _get_redis()
                if r_server.exists(py_key):
                    object = _search_redis(py_key)
                    mapping = {
                        'char_keys': "".join( (object['char_keys'], ',', char_key) ),   
                    }
                    r_server.hmset(py_key, mapping)
                                        
                else:
                    mapping = {
                        'char_keys': char_key,
                        'id': uuid.uuid4().hex,
                    }
                    r_server.hmset(py_key, mapping)                    
    
    
                # ADD THE CHARACTER ENTRY
                if r_server.exists(char_key):
                     
                    object = _search_redis(char_key)
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
                        r_server.hmset(char_key, mapping)
                            
                else:
                    mapping = {
                        'chars': new[1],
                        'pinyin1': tonal_pinyin, 
                        'meaning1': meanings,
                        'count': 1,
                        'id': uuid.uuid4().hex,
                    }
                    
                    r_server.hmset(char_key, mapping)
                
                item_count += 1
                print item_count
                               
        
        print "%s Chinese items added" % item_count          
        file.close()        


"""


 
"""