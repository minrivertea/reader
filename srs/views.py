#!/usr/bin/python
# -*- coding: utf8 -*-


from django.template.loader import render_to_string
from django.utils.encoding import smart_unicode
from django.template import RequestContext
from django.http import HttpResponse

# python
import time

from cedict.words import ChineseWord
from utils.helpers import _render
from forms import SubmitAnswerForm


    
    
def review_new(request):

    words = request.user.get_review_items()
    items = []
    for x in words:
        thing = {}
        thing['word'] = ChineseWord(chars=x['chars'])
        thing['personal'] = x
        items.append(thing)
        
    return _render(request, 'srs/review_new.html', locals())



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


def submit_answer(request):
    
    if request.method == 'POST':
        form = SubmitAnswerForm(request.POST)
        if form.is_valid():
            
            word = ChineseWord(chars=form.cleaned_data['characters'])
            meanings_count = len(word.meanings)
            
            pinyin_pass = True
            meaning_pass = True
            
            # create a list of the expected values for a correct answer
            data = form.cleaned_data
            possibles = []
            count = 1
            while meanings_count != 0:
                possibles.append(('pinyin_%s' % count))
                possibles.append(('meaning_%s' % count ))
                count += 1
                meanings_count -= 1


            # check if the provided answers match the correct answers
            results = {}
            results['pinyin_pass'] = False
            results['meaning_pass'] = False
            results['character_pass'] = True
            results['test_date'] = time.time()
            for x in possibles:
                if x in data:
                    if data[x] == data["".join((x, '_answer'))]:
                        if 'pinyin' in x:
                            results['pinyin_pass'] = True   
                        elif 'meaning' in x:
                            results['meaning_pass'] = True
            
            request.user.get_personal_words()._update_word(word.chars, test_results=results)
            
                                
            if request.is_ajax():
                return HttpResponse('OK')
        
        else:
            # BUG: THIS SHOULD RETURN OR DO SOMETHING
            print form.errors
            print "invalid form"
    
    
    
    return HttpResponse()