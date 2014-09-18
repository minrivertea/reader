#!/usr/bin/python
# -*- coding: utf8 -*-


from django.template.loader import render_to_string
from django.utils.encoding import smart_unicode
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# python
import time

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
                  
        # IS THIS THE FIRST TEST
        word = ChineseWord(chars=x['chars'])
        word.id = count
        for m in word.meanings:
            
            chinese_word = ChineseWord()._get_random(number=1, chars=x['chars'])['meanings'][0]['meaning']
            
            m['alternative_meaning'] = chinese_word
            
        html = render_to_string('srs/tests/first_test.html', {'word': word, 'form': SubmitAnswerForm()}, context_instance=RequestContext(request))
        
                    

        # if we get here, add it to the items list
        if html:
            count += 1
            items.append(html)
                
    return _render(request, 'srs/test.html', locals())


@login_required
def submit_answer(request):
    
    if request.method == 'POST':
        form = SubmitAnswerForm(request.POST)
        if form.is_valid():
                       
            # setup some variables
            data = form.cleaned_data
            results = {}
            results['character_pass'] = True
            testing = ['pinyin', 'meaning']
            
            # let's see if they got it right!
            

            for y in testing:
                count = 1
                key = '%s_pass' % y
                while data[('%s_%s_answer' % (y, count))]:
                    
                    if data[('%s_%s' % (y, count))] == data[('%s_%s_answer' % (y, count))]:
                        results[key] = True
                        request.user.no_correct += 1
                    else:
                        results[key] = False
                        request.user.no_wrong += 1
                    count += 1
                
            # update the user information
            request.user.items_to_test -= 1
            request.user.save()
            request.user.get_personal_words()._update_word(data['characters'], test_results=results)
                        
                                
            if request.is_ajax():
                return HttpResponse('OK')
        
        else:
            # BUG: THIS SHOULD RETURN OR DO SOMETHING
            print form.errors
            print "invalid form"
    
    
    
    return HttpResponse()