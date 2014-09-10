#!/usr/bin/python
# -*- coding: utf8 -*-

from django.conf import settings

from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

import uuid
import json
import re
from django.utils.encoding import smart_str, smart_unicode



# import various bits and pieces
from utils.redis_helper import _get_redis, _search_redis, _add_to_redis

from cjklib import characterlookup
from cjklib.dictionary import *
from cjklib.reading import ReadingFactory


# this sends out the first 'review' email after the order was shipped.
class Command(NoArgsCommand):
    
    help = 'Updates the dictionary with any new entries or things missed first time around'    

    def handle_noargs(self, **options):
        # 一事無成 一事无成 [yi1 shi4 wu2 cheng2] /to have achieved nothing/to be a total failure/to get nowhere/

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
                

                    
                    
                    
                
                py_key = settings.PINYIN_WORD_KEY % (len(num_pinyin.split(' ')), num_pinyin.replace(' ', '_'))
                char_key = settings.CHINESE_WORD_KEY % ((len((characters))/3), characters) 
                
                # CREATE THE PRONUNCIATION/MEANING PAIR
                pair = {}
                pair['pinyin'] = tonal_pinyin
                pair['meaning'] = meanings
                pair['measure_words'] = mws
                
                
                # ADD THE PINYIN ENTRY
                # --------------------
                
                if not _search_redis(py_key, lookup=False):
                    values = [characters,]
                    r_server.set(py_key, json.dumps(values))                    
    
    
    
    
                # ADD THE CHINESE CHARACTER ENTRY
                # -------------------------------
                if not r_server.exists(char_key):
                    values = {
                        'chars': characters,
                        'meanings': [pair,],
                    }
                    
                    r_server.set(char_key, json.dumps(values))
                
                    item_count += 1
                    print item_count
                
                               
        
        print "%s Chinese items updated" % item_count          
        file.close()        


"""


 
"""