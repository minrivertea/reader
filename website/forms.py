from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

 
            
class SearchForm(forms.Form):
    char = forms.CharField(widget=forms.Textarea, required=True, error_messages={'required': '* Please enter a character'})
    

