#!/usr/bin/python
# -*- coding: utf8 -*-

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import smart_unicode
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# python
import time
import random
import string

from cedict.words import ChineseWord
from utils.helpers import _render
from forms import SubmitAnswerForm


    
@login_required   
def review_new(request):

    words = request.user.get_review_items()
    items = []
    for x in words:
        thing = {}
        thing['word'] = ChineseWord(chars=x['chars'])
        thing['personal'] = x
        items.append(thing)
        
    return _render(request, 'srs/review_new.html', locals())


def _alt_pinyin(pinyin):
    
    x = ['1','2','3','4']; random.shuffle(x)
    tbl = string.maketrans("".join(x), '1234')
    new_pinyin = str(pinyin).translate(tbl)

    return new_pinyin


def _alt_chars(chars):
    
    
    return chars
    

@login_required
def test(request):
    
    # COLLECT THE WORDS
    words = request.user.get_test_items()
        
    # DECIDE HOW TO TEST THE ITEMS
    items = []
    count = 1
    for x in words:

        to_test = []
        testing = ['pinyin', 'characters', 'meaning']  
               
        
        for t in testing:
            
            # work out what level we should test this item at
            level = int( x.get(('%s_test_level' % t), 0))
            if level < settings.MAX_TEST_LEVEL and x.get(('%s_pass' % t), False):
                level += 1
            
            # setup some values           
            vals = {}
            vals['level'] = level
            vals['testing'] = t
            to_test.append(vals)
        
        # randomly decide which item to test this time.
        test = random.choice(to_test)
        word = ChineseWord(chars=x['chars'])
        
                
        # PREPARE THE CHOICES
        for m in word.meanings:
            
            test['choices'] = []
            test['chars'] = word.chars
            
            # PINYIN CHOICES
            if test['testing'] == 'pinyin':
                
                test['main'] = word.chars
                test['other'] = m['meaning']
                test['answer'] = m['pinyin']
                
                test['choices'].append(m['pinyin_numbered'])
                
                
                # EASY
                if test['level'] == 0:
                    new = ChineseWord()._get_random(number=1, chars=word.chars)['meanings'][0]
                    test['choices'].append(new['pinyin_numbered'])
                
                # MEDIUM
                if test['level'] == 1:
                    test['choices'].append( _alt_pinyin(m['pinyin_numbered']) )
                    
        
            # CHARACTER CHOICES
            if test['testing'] == 'characters':
                
                test['main'] = m['pinyin']
                test['other'] = m['meaning']
                test['answer'] = word.chars
                test['choices'].append(word.chars)
                
                # EASY
                if test['level'] == 0:
                    new = ChineseWord()._get_random(number=1, chars=word.chars)
                    test['choices'].append( new['chars'] )
                
                # MEDIUM
                if test['level'] == 1:
                    new = ChineseWord()._get_random(number=1, chars=word.chars)
                    test['choices'].append( new['chars'] )
            
            
            # MEANING CHOICES
            if test['testing'] == 'meaning':
                test['main'] = word.chars
                test['other'] = m['pinyin']
                test['answer'] = m['meaning']
                test['choices'].append(m['meaning'])
                
                # EASY
                if test['level'] == 0:
                    new = ChineseWord()._get_random(number=1, chars=word.chars)['meanings'][0]
                    test['choices'].append( new['meaning'] )
                
                # MEDIUM
                if test['level'] == 1:
                    new = ChineseWord()._get_random(number=1, chars=word.chars)['meanings'][0]
                    test['choices'].append( new['meaning'] )
            
            random.shuffle(test['choices'])
                
        
                       
        html = render_to_string(
            'srs/tests/base_test.html', 
            {'test': test,}, 
            context_instance=RequestContext(request)
        )
        

        # if we get here, add it to the items list
        if html:
            count += 1
            items.append(html)
                
    return _render(request, 'srs/test.html', locals())


@login_required
def submit_answer(request):
    
    if request.method == 'POST':
        
        request.user.get_personal_words()._update_word(request.POST['chars'], test_results=request.POST)            
                            
        if request.is_ajax():
            return HttpResponse('OK')
        
    return HttpResponse()
    
    
    
    
    
    
    
    