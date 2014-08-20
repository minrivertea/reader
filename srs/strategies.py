#!/usr/bin/python
# -*- coding: utf8 -*-

import datetime
import time

from users.models import User
from utils.redis_helper import _search_redis
from cedict.words import ChineseWord


class BaseStrategy(object):
   
   def __init__(self, email):
       """ We must start with a user """
       self.user = User.objects.get(email=email)
   
   

class ReviewNew(BaseStrategy):
    """ Show recent words added to personal dictionary """
    
    description = "Read and review these words again, looking over the characters, sounds and meanings. Spend a 3-4 minutes maximum and read them out aloud if it's convenient. Don't try to test yourself yet!"
    empty_description = "You've got no items left to review right now"
    
    def items(self, exclusions=[]):
        """ Get the items for this strategy """
        
        # get the list and sort it
        wordlist = self.user.get_personal_words().get_items(review=True, timestamp=time.time())
        wordlist.sort(key=lambda x: x['search_date'], reverse=False)
                
        words = []
        for x in wordlist:
                                    
            # if this word is in our excluded list, we'll now slice the words list
            # from this point. This is a trick to make sure we don't return the same
            # words to a user if they do multiple 'exchanges' when reviewing items
            count = 0
            if x['chars'] in exclusions:                
                count = len(words)
                words = words[count:]
                continue

            # add the word if we've got here
            words.append(ChineseWord(chars=x['chars']))
            
            # when we have enough words, break
            if len(words) == self.user.test_items_limit:
                break
        
        return words
    
    def _exchange_word(self, word, exclusions=[]):
        
        exclusions.append(word)
        
        try:
            word = self.items(exclusions=exclusions)[(self.user.test_items_limit-1)]
        except IndexError:
            word = None
                        
        return word


class FirstTest(BaseStrategy):
    
    title = "Fill in the gaps"
    description = "Try to remember the words and fill in the gaps. "
    empty_description = "There's nothing to test right now!"
    
    
    def items(self, exclusions=[]):
        """ Get the items for this strategy """
        
        
        wordlist = self.user.get_personal_words().words
        
        # turn it into a list - possibly bad...
        words_list = []
        for x,v in wordlist.iteritems():
            v['chars'] = x
            words_list.append(v)
        
        words = []
        for x in words_list:
            
            # exclude those that haven't been reviewed yet
            if 'review_count' in x:
                if x['review_count'] == 0:
                    continue
            
            
            words.append(ChineseWord(chars=x['chars']))
        
        return words  
    
    
        
     