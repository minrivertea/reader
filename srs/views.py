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
from strategies import *
from forms import SubmitAnswerForm


    
    
def review_new(request):

    strategy = ReviewNew(request.user.email)
    
    return _render(request, 'srs/review_new.html', locals())



def test(request):
    
    # get words ready to test today
    words = request.user.get_personal_words().get_items(test=True) #, timestamp=time.time())
        
    # now we need to decide how to test each item.
    items = []
    count = 1
    for x in words:
        html = None        
        # is this the first time we've tested it?
        if not x['test_date']:
            word = ChineseWord(chars=x['chars'])
            word.id = count
            for m in word.meanings:
                m['alternative_meaning'] = ChineseWord()._get_random(number=1, chars=x['chars'])['meaning1']
                
            html = render_to_string('srs/tests/first_test.html', {'word': word, 'form': SubmitAnswerForm()}, context_instance=RequestContext(request))
                     
        
        if x['character_pass'] and x['pinyin_pass'] and x['meaning_pass']:
            continue

        # if we get here, add it to the items list
        if html:
            count += 1
            items.append(html)
            
    print html
    
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
            print form.errors
            print "invalid form"
    
    
    
    return HttpResponse()