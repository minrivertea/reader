from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

 
            
class SearchForm(forms.Form):
    char = forms.CharField(widget=forms.Textarea, required=True, error_messages={'required': '* Please enter a character'})
    


attrs_dict = {'class': 'required clearMeFocus'}        
    
class SimpleRegistrationForm(forms.Form):
    """
    A registration form that will work with django-registration package
    but that doesn't require separate username and emails. It's built
    to work with the custom backend in the reader project, which automatically
    cludges the username/email for django.
    """
    
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_("Email"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("Password"))
    
