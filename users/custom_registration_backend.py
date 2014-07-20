from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from django import forms
from django.utils.translation import ugettext_lazy as _


from registration import signals
from registration.models import RegistrationProfile
from registration.views import RegistrationView 
from registration.forms import RegistrationForm


from users.models import User


class CustomRegistrationForm(forms.Form):

    required_css_class = 'required'

    email = forms.EmailField(label=_("E-mail"))
    password1 = forms.CharField(widget=forms.PasswordInput,
                                label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label=_("Password (again)"))
    
    def clean_email(self):
        """
        Validate that the email is unique and not already in user
        
        """
        existing = User.objects.filter(email__iexact=self.cleaned_data['email'])
        if existing.exists():
            raise forms.ValidationError(_("An account with that email already exists."))
        else:
            return self.cleaned_data['email']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data
        
        

class CustomRegistrationView(RegistrationView):
    """
    A registration backend which follows a simple workflow:

    1. User signs up, inactive account is created.

    2. Email is sent to user with activation link.

    3. User clicks activation link, account is now active.

    """
    
    def register(self, request, **cleaned_data):

        email, password = cleaned_data['email'], cleaned_data['password1']
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        username = email
        new_user = RegistrationProfile.objects.create_inactive_user(username, email,
                                                                    password, site)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user

    def registration_allowed(self, request):
        """
        Indicate whether account registration is currently permitted,
        based on the value of the setting ``REGISTRATION_OPEN``. This
        is determined as follows:

        * If ``REGISTRATION_OPEN`` is not specified in settings, or is
          set to ``True``, registration is permitted.

        * If ``REGISTRATION_OPEN`` is both specified and set to
          ``False``, registration is not permitted.
        
        """
        return getattr(settings, 'REGISTRATION_OPEN', True)

    # define the custom registration form class
    def get_form_class(self, request=None):
        return CustomRegistrationForm
    
    def get_success_url(self, request, user):
        """
        Return the name of the URL to redirect to after successful
        user registration.
        
        """
        return ('registration_complete', (), {})

