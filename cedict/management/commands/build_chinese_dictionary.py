#!/usr/bin/python
# -*- coding: utf8 -*-

from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError
from django.utils.encoding import smart_str, smart_unicode

import json


# import various bits and pieces
from utils.redis_helper import _get_redis, _search_redis, _add_to_redis
from utils.helpers import _normalize_pinyin, _pinyin_to_ascii

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
        'chars': '好',        
        'trad_chars': '好',
        'hsk_level': '', # future
        'measure_word': '个' # eg. if it's a noun with a measure word
        'meanings': [
            {'pinyin': 'hao', 'meaning': 'okay, yes', 'weight':'1'},
            {'pinyin': 'hao', 'meaning': 'I suppose so', 'weight':'2'}            
        ]
        'startswith': [
            '好吧', '好汉', '好的'...
        ]
        'contains': [
            
        ]
    }
    
    This is all coded into JSON and then dumped as a string into Redis, so that
    we can easily JSON.loads it on the way out and use it nicely.  
    
    A pinyin entry has a key like "PY:haoba" is something like this:
    
    {
       '好吧',
       '毫巴',        
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
                
                # OPEN REDIS CONNECTION NOW
                r_server = _get_redis()
                
                # GATHER ALL THE MAIN VARIABLES
                new = line.split()
                numbered_pinyin = line[(line.index('[')+1):(line.index(']'))]
                f = ReadingFactory()
                tonal_pinyin =  f.convert(numbered_pinyin, 'Pinyin', 'Pinyin',
                    sourceOptions={'toneMarkType': 'numbers', 'yVowel': 'v',
                    'missingToneMark': 'fifth'})
                meanings = line[(line.index('/')+1):(line.rindex('/'))]               
                characters = new[1]
                
                # REMOVE ALL THE UGLY CHARACTERS
                if '，' in characters:
                    characters = characters.replace('，', '')
                
                
                # GET AND CLEAN THE MEASURE WORD
                mws = None
                if "CL:" in meanings:
                    new_meanings = meanings.split('/')
                    for idx, val in enumerate(new_meanings):
                        if "CL:" in val:
                            mws = []
                            for x in val.replace('CL:', '').split(','):
                                
                                x = x[:(x.index('['))]
                                if '|' in x:
                                    x = x[(x.index('|')+1):]
                                    
                                    
                                # ADD THE MEAASURE WORDS ENTRY
                                # ----------------------------
                                mws_key = settings.MEASURE_WORD_KEY % x   
                                if r_server.exists(mws_key):
                                    values = json.loads(_search_redis(mws_key))
                                    values['chars'].append(characters)
                                else:
                                    values = {'chars': [characters,]}
                                r_server.set(mws_key, json.dumps(values))                                
                                    
                                mws.append(x)
                            
                            
                            
                            new_meanings.pop(idx)
                    meanings = "/".join(new_meanings)
                

                    
                    
                    
                
                
                
                char_key = settings.CHINESE_WORD_KEY % ((len((characters))/3), characters)                 
                
                # CREATE THE PRONUNCIATION/MEANING PAIR
                pair = {}
                pair['pinyin'] = tonal_pinyin
                pair['pinyin_numbered'] = _normalize_pinyin(numbered_pinyin)
                pair['meaning'] = meanings
                pair['measure_words'] = mws
                
                
                
                # ADD THE PINYIN ENTRY
                # --------------------
                
                py_key = settings.PINYIN_WORD_KEY % _pinyin_to_ascii(numbered_pinyin)
                if r_server.exists(py_key):
                    values = json.loads(_search_redis(py_key))
                    if smart_unicode(characters) not in values:
                        values.append(characters)
                else:
                    values = [characters,]
                
                r_server.set(py_key, json.dumps(values))                    
    
    
    
    
                # ADD THE CHINESE CHARACTER ENTRY
                # -------------------------------
                if r_server.exists(char_key):
                    values = json.loads(_search_redis(char_key))
                    values['meanings'].append(pair)
                else:
                    values = {
                        'chars': characters,
                        'meanings': [pair,],
                    }
                    
                r_server.set(char_key, json.dumps(values))
                
                item_count += 1
                print item_count

                
                               
        
        print "%s Chinese items added" % item_count          
        file.close()        


"""


 
"""