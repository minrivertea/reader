from django import forms
from django.forms import ModelForm

 
            
# handles the submission of their personal details during the order process
class CheckPinyinForm(forms.Form):
    char = forms.CharField(widget=forms.Textarea, required=True, error_messages={'required': '* Please enter a character'})
    