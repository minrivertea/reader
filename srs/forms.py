from django import forms

            
class SubmitAnswerForm(forms.Form):
    
    characters = forms.CharField(required=False)
    
    # possible meanings
    meaning_1_answer = forms.CharField(required=False)
    meaning_1 = forms.CharField(widget=forms.RadioSelect(), required=False)
    meaning_2_answer = forms.CharField(required=False)
    meaning_2 = forms.CharField(widget=forms.RadioSelect(), required=False)    
    meaning_3_answer = forms.CharField(required=False)
    meaning_3 = forms.CharField(widget=forms.RadioSelect(), required=False)
    meaning_4_answer = forms.CharField(required=False)
    meaning_4 = forms.CharField(widget=forms.RadioSelect(), required=False)
    
    # possible pinyin    
    pinyin_1_answer = forms.CharField(required=False)
    pinyin_1 = forms.CharField(required=False)
    pinyin_2_answer = forms.CharField(required=False)
    pinyin_2 = forms.CharField(required=False)    
    pinyin_3_answer = forms.CharField(required=False)
    pinyin_3 = forms.CharField(required=False)
    pinyin_4_answer = forms.CharField(required=False)
    pinyin_4 = forms.CharField(required=False)
    
    
   
    

