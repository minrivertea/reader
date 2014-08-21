#!/usr/bin/python
# -*- coding: utf8 -*-

import string, unicodedata
import os
PROJECT_PATH = os.path.normpath(os.path.dirname(__file__))

from django.conf import settings
from django.template import RequestContext, TemplateDoesNotExist
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.http import HttpResponseRedirect, HttpResponse, Http404

from cedict.pinyin import PINYIN_WORDS, AMBIGUOUS_WORDS

from cjklib.reading import *


#render shortcut
def _render(request, template, context_dict=None, page=None, **kwargs):
    
    # HANDLE THE REQUEST WITH AJAX
    if request.is_ajax():
       
        html = render_to_string(template, context_dict or {}, 
            context_instance=RequestContext(request), **kwargs)
        
        return HttpResponse(html)
        
    else:
        context_dict['snippet'] = template
        template = 'generic_parent.html'
    
    return render_to_response(
        template, context_dict or {}, context_instance=RequestContext(request),
            **kwargs)  


from re import compile as _Re
_unicode_chr_splitter = _Re( '(?s)((?:[\ud800-\udbff][\udc00-\udfff])|.)' ).split
def _split_unicode_chrs(text):
    return [ chr for chr in _unicode_chr_splitter( text ) if chr ]


def _is_punctuation(x):
    
    try:
        if x in string.whitespace:
            return True
            
        if x in string.punctuation:
            return True
                
        if unicodedata.category(x).startswith(('P', 'Z', 'S')):
            return True
            
    except:
        pass
    
    return False

def _is_number(x):
    for t in x:
        if t.isdigit() or unicodedata.category(t).startswith('N'):
            return True
        try:
            float(t)
            return True
        except ValueError:
            return False
    return False


def _is_english(x):
    
    if len(x) > 1:
        for y in x:
            if y in string.ascii_letters:
                return True
        
    if x in string.ascii_letters:
        return True
    
    return False

def _is_ambiguous(x):

    count = 0
    for thing in x.split(' '):
        if thing in AMBIGUOUS_WORDS:
            count += 1
       
    if count == len(x.split(' ')):
        return True
            
    return False


# RETURNS A NICELY FORMATTED HTML BREADCRUMB
def _get_crumbs(request):
    
    try:
        crumbs = request.session['crumbs']
    except:
        crumbs = ''
        request.session['crumbs'] = crumbs
        return crumbs
    
    items = []
    loop = 0
    objects = crumbs.split(' \ ')
    for x in objects:
        try:
            next = objects[loop+1]
            url = reverse('single_word', args=[x])
            string = '<a href="%s">%s</a>' % (url, x)
        except:
            string = x
        items.append(string)
        loop += 1
    
    crumbs_html = ' \ '.join(items) 
    return crumbs_html

# CHECKS IF THE INCOMING STRING IS PINYIN OR NOT
def _is_pinyin(x):
    
    for thing in x.split(' '):
        try:
            # CLEAN THE PINYIN INTO NUMBERED PINYIN AND THEN STRIP THE NUMBERS
            # AND THEN COMPARE TO OUR LIST OF PINYIN WORDS            
            if filter(lambda x: x not in '12345', _clean_pinyin(thing)) in PINYIN_WORDS:
                return True
        except:
            pass      


    return False


def _clean_pinyin(x):
    """
    Filters any incoming pinyin, regardless of what format and then 
    spits out standardised numbered pinyin eg. takes something like 
    "nǚháizi" and returns "nv3 hai2 zi5". If it gets something that
    isn't pinyin, it won't handle it. The function calling _clean_pinyin
    should handle any errors.
    """
    
    f = ReadingFactory()
    pinyin = None
    
    # IF THE INPUT IS NUMBERED PINYIN (eg. 'nü3') THEN DO THIS
    if filter(lambda y: y not in '12345', x) != x:
        pinyin = f.convert(x, 'Pinyin', 'Pinyin', 
            sourceOptions={'toneMarkType': 'numbers', 'missingToneMark': 'fifth',},
            targetOptions={'toneMarkType': 'numbers', 'yVowel': 'v',}
        )
    
    # IF THE INPUT IS SUPER PLAIN-JANE PINYIN (eg. 'nv' or 'nu') THEN DO THIS
    if len(filter(lambda x: x not in ("".join((string.ascii_letters, u'ü', ' ', '_'))), x)) == 0:
        pinyin = f.convert(x, 'Pinyin', 'Pinyin', 
            sourceOptions={'toneMarkType': 'numbers',},
            targetOptions={'toneMarkType': 'numbers', 'missingToneMark': 'noinfo', 'yVowel': 'v',}
        )
         
    # IF THE INPUT IS TONAL PINYIN (eg. nǚ hái zi)  
    if not pinyin:
        pinyin = f.convert(x, 'Pinyin', 'Pinyin', 
            sourceOptions={'missingToneMark': 'noinfo'}, 
            targetOptions={'toneMarkType': 'numbers', 'missingToneMark': 'noinfo', 'yVowel': 'v'}
        )

    return pinyin


# ADD OR REMOVE ITEMS FROM THE BREADCRUMB    
def _update_crumbs(request, word=None):
        
    try:
        crumbs = request.session['crumbs']
    except:
        crumbs = ''
        request.session['crumbs'] = crumbs
        return crumbs
    
    
    if word == None:
        crumbs = ''
        request.session['crumbs'] = crumbs
        return crumbs
    
    if word == crumbs.split(' \ ')[-1]:
        return crumbs
    
    match = False
    loop = 0
    for x in crumbs.split(' \ '):
        if word == x:
            match = True
            break
        else:
            match = False
            loop +1
    
    if match == True:
        head, sep, tail = crumbs.partition(word)
        new_crumb = "%s%s" % (head, sep)
    else:
        new_crumb = "%s \ %s" % (crumbs, word)
    
    request.session['crumbs'] = new_crumb
    return new_crumb



def _send_email(recipient, subject_line, template, extra_context=None, sender=None, admin=False):
     
    # CREATE THE MESSAGE BODY FROM THE TEMPLATE AND CONTEXT
    extra_context = extra_context or {}
    email_signature = render_to_string(
        'emails/email_signature.txt', 
        {'site_name': settings.SITE_NAME, 'site_url': settings.SITE_URL,}
    )
    html_email_signature = render_to_string(
        'emails/email_signature.html', 
        {'site_name': settings.SITE_NAME, 'site_url': settings.SITE_URL,}
    )
    context = {
        'EMAIL_SIGNATURE': email_signature,
        'HTML_EMAIL_SIGNATURE': html_email_signature,
        'static_url': settings.STATIC_URL,
        'SITE_NAME': settings.SITE_NAME,
        'site_name': settings.SITE_NAME,
        'SITE_URL': settings.SITE_URL,
        'site_url': settings.SITE_URL,
        'SUBJECT_LINE': subject_line,
        'email_base_template': settings.EMAIL_BASE_HTML_TEMPLATE
    }
    
    context = dict(context.items() + extra_context.items())
    
    # MODIFY THE RECIPIENTS IF ITS AN ADMIN EMAIL
    if admin:
        recipient = [x[1] for x in settings.NOTIFICATIONS_GROUP]
    else:
        recipient = [recipient]
        
    # WHO IS SENDING IT?
    if sender:
        sender = sender
    else:
        sender = settings.SITE_EMAIL
        
    # CHECK IF THERE'S AN HTML TEMPLATE?
    text_content = render_to_string(template, context)
    html_content = None
    try:
        html_template_name = template.replace('.txt', '.html')
        html_content = render_to_string(html_template_name, context)
    except TemplateDoesNotExist:
        pass
    
    # HERE IS THE ACTUAL MESSAGE NOW
    msg = EmailMultiAlternatives(subject_line, text_content, sender, recipient)    

    if html_content:
        # USING PREMAILER TO PUT STYLES INLINE FOR CRAPPY YAHOO AND AOL WHO STRIP STYLES
        from premailer import transform
        html_content = transform(html_content)
        msg.attach_alternative(html_content, "text/html")
        # msg.content_subtype = "html" # DONT DO THIS!
    
    
    msg.send()
    return True



    
    
    
    
    
    
    
    
    
    
    
        

