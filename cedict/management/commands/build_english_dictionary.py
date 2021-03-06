#!/usr/bin/python
# -*- coding: utf8 -*-

from django.conf import settings

from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

import string
import json



# import various bits and pieces
from utils.redis_helper import _get_redis, _search_redis, _add_to_redis

from cjklib import characterlookup
from cjklib.dictionary import *
from cjklib.reading import ReadingFactory


EXCLUSIONS = [
    "same as",
    "variant of",
    "variant for",
    "contraction of", 
    "radical in Chinese characters",
    "component in Chinese character",
    "also written", 
]



# this sends out the first 'review' email after the order was shipped.
class Command(NoArgsCommand):
    help = 'This builds from scratch the English-Chinese dictionary'

    def handle_noargs(self, **options):
        # EXAMPLE: 一中一台 [yi1 Zhong1 yi1 Tai2] /first meaning/second meaning/
        file = open(settings.DICT_FILE_LOCATION)
        r_server = _get_redis()
        
        # EMPTY ALL EN KEYS FROM THE DATABASE
        item_count = 0
        keys = r_server.keys('EN:*')
        for x in keys:
            r_server.delete(x)
            item_count += 1
        print "Deleted %s items" % item_count
        
        
        # NOW LETS START
        item_count = 0
        for line in file:
            if not line.startswith("#"):

                # GATHER ALL THE MAIN VARIABLES
                new = line.split()
                characters = new[1]
                numbered_pinyin = line[(line.index('[')+1):(line.index(']'))]
                f = ReadingFactory()
                tonal_pinyin =  f.convert(numbered_pinyin, 'Pinyin', 'Pinyin',
                    sourceOptions={'toneMarkType': 'numbers', 'yVowel': 'v',
                    'missingToneMark': 'fifth'})
                meanings = line[(line.index('/')+1):(line.rindex('/'))]               
                
                # CREATE AN INDEX: What we'll do first is try to strip out
                # as much crap as possible from each definition, and as close as
                # possible find a single word that we can index on.
                
                for x in meanings.split('/'):
                    
                    ns = x # new_string
                    
                    # REMOVE ANYTHING BETWEEN BRACKETS
                    try:
                        ns = ns.replace(ns[(ns.index('(')+1):(ns.index(')'))], '')
                        ns = ns.replace('(', '').replace(')', '') #replace the brackets too
                    except ValueError:
                        pass
                    
                    # REMOVE ANYTHING BETWEEN SQUARE BRACKETS
                    try:
                        ns = ns.replace(ns[(ns.index('[')+1):(ns.index(']'))], '')
                        ns = ns.replace('[', '').replace(']', '') #replace the brackets too
                    except ValueError:
                        pass
                    
                    # IGNORE THE MEANING IF IT CONTAINS AN EXCLUDED PHRASE 
                    if len(filter(lambda y: y not in ns, EXCLUSIONS)) != len(EXCLUSIONS):
                        continue
                                        
                    # IF THE MEANING IS NOW EMPTY, IGNORE IT
                    ns = ns.strip()
                    if ns == '':
                        continue
                    
                    # DEAL WITH INFINITIVE VERBS LIKE "TO DO" WITH 2 WORDS
                    if len(ns.split(' ')) <= 3 and ns.startswith('to '):
                        ns = ns.split(' ', 1)[1]
                    
                    # REMOVE ITEMS LIKE "SEE XYZ"
                    if ns.split(' ')[0] == 'see' and ns[-1] not in string.ascii_letters:
                        continue
                    
                    # THERE'S ALSO SOME ANNOYING "..." MARKS TOO
                    if "..." in ns:
                        ns = ns.replace('...', '')                    
                    
                    
                    # FOR NOW, JUST ADD ITEMS WITH 2 WORDs
                    if len(ns.split(' ')) <= 3:
                        
                        key = "EN:%sW:%s" % (len(ns.split(' ')), ns.lower())
                        print key
                        if r_server.exists(key):
                            values = json.loads(_search_redis(key))
                            values['characters'].append(characters)
                            r_server.set(key, json.dumps(values))

                        else:
                            
                            values = {
                                'english': x,
                                'characters': [characters,],
                            }
                            
                            r_server.set(key, json.dumps(values))
                        
                        item_count += 1
                        print item_count
                        
            #if item_count > 20:
            #    break
                                        
                    
                
                
                
                                
        
        print "%s English dictionary items added" % item_count          
        file.close()        


"""


 
"""