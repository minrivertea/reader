from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

 
            
# handles the submission of their personal details during the order process
class CheckPinyinForm(forms.Form):
    char = forms.CharField(widget=forms.Textarea, required=True, error_messages={'required': '* Please enter a character'})
    

# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary. If/when Django ticket #3515
# lands in trunk, this will no longer be necessary.
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
    
