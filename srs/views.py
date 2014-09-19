#!/usr/bin/python
# -*- coding: utf8 -*-


from django.template.loader import render_to_string
from django.utils.encoding import smart_unicode
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# python
import time
import random

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


@login_required
def test(request):
    
    # COLLECT THE WORDS
    words = request.user.get_test_items()
        
    # DECIDE HOW TO TEST THE ITEMS
    items = []
    count = 1
    for x in words:

        templates = []
        max_level = 1
        testing = ['pinyin', 'characters', 'meaning']        
        
        for t in testing:
            
            if x.get(('%s_pass' % t), False):
                level = int( x.get(('%s_test_level' % t), 0)) + 1
            else:
                level = x.get(('%s_test_level' % t), 0)
            
            if level > max_level:
                level = max_level
                
            templates.append('srs/tests/%s_%s.html' % (t, level))
            

        word = ChineseWord(chars=x['chars'])
        word.id = count
        for m in word.meanings:
            
            chinese_word = ChineseWord()._get_random(number=1, chars=x['chars'])
            
            m['alternative_meaning'] = chinese_word['meanings'][0]['meaning']
            m['alternative_pinyin'] = chinese_word['meanings'][0]['pinyin']
            m['alternative_characters'] = chinese_word['chars']
            
        
        template = random.choice(templates)    
        html = render_to_string(template, {'word': word, 'form': SubmitAnswerForm()}, context_instance=RequestContext(request))
        
                    

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
    
    
    
    
    
    
    
    