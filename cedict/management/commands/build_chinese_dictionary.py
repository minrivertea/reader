#!/usr/bin/python
# -*- coding: utf8 -*-

from django.conf import settings

from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

import uuid
import json


# import various bits and pieces
from utils.redis_helper import _get_redis, _search_redis, _add_to_redis

from cjklib import characterlookup
from cjklib.dictionary import *
from cjklib.reading import ReadingFactory


# this sends out the first 'review' email after the order was shipped.
class Command(NoArgsCommand):
    """ 
    We're going to build the Chinese character dictionary. There's around
    100k individual entries. Each one has a key like "ZH:2C:好吧" and corresponds
    to a value like this:
    
    {
        'chars': '好吧',        
        'trad_chars': '好吧',
        'hsk_level': '', # leave empty for the moment
        'meanings': [
            {'pinyin': 'hao ba', 'meaning': 'okay, yes', 'weight':'1'},
            {'pinyin': 'hao ba', 'meaning': 'I suppose so', 'weight':'2'}            
        ]
    }
    
    This is all coded into JSON and then dumped as a string into Redis, so that
    we can easily JSON.loads it on the way out and use it nicely.  
    
    A pinyin entry has a key like "PY:2W:hao3_ba1" is something like this:
    
    {
       'words': ['好吧', '毫巴',]        
    }
      
    """
    
    
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
                characters = new[1]
                
                # REMOVE ALL THE UGLY CHARACTERS
                if '，' in characters:
                    characters = characters.replace('，', '')
                
                
                py_key = settings.PINYIN_WORD_KEY % (len(num_pinyin.split(' ')), num_pinyin.replace(' ', '_'))
                char_key = settings.CHINESE_WORD_KEY % ((len((characters))/3), characters) 
                
                
                # ADD THE PINYIN ENTRY
                # --------------------
                r_server = _get_redis()
                if _search_redis(py_key, lookup=False):
                    values = json.loads(_search_redis(py_key))
                    values.append(characters)
                    r_server.set(py_key, json.dumps(values))
                else:
                    values = [characters,]
                    r_server.set(py_key, json.dumps(values))                    
    
    
    
    
                # ADD THE CHINESE CHARACTER ENTRY
                # -------------------------------
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
                        'chars': characters,
                        'pinyin1': tonal_pinyin, 
                        'meaning1': meanings,
                        'count': 1,
                    }
                    
                    r_server.hmset(char_key, mapping)
                
                item_count += 1
                print item_count
                               
        
        print "%s Chinese items added" % item_count          
        file.close()        


"""


 
"""