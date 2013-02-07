# -*- coding: utf-8 -*-
"""
This module provides the form-classes (definition) for the basic models, especially Quest, Adventure and Userprofile.
"""
import datetime
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django import forms
from django.core.urlresolvers import reverse

from django.utils.translation import ugettext_lazy as _

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, Button, BaseInput
from registration.forms import RegistrationFormUniqueEmail

from herobase.models import Quest, UserProfile
from herobase.widgets import LocationWidget




class QuestCreateForm(forms.ModelForm):
    """The Basic Quest create form. Uses django-crispy-forms (FormHelper) for 2 column bootstrap output. """
    remote = forms.ChoiceField(choices=(
        ("", _("-----------")),
        (True, _(u"Can be done remotely")),
        (False, _(u"Has to be done locally"))
    ), help_text=_(u"Can this quest be done remotely or only locally?"),
    )
    # latitude = forms.FloatField(widget=forms.HiddenInput, required=False)
    # longitude = forms.FloatField(widget=forms.HiddenInput, required=False)
    # address = forms.CharField(widget=LocationWidget("id_latitude", "id_longitude", "id_location_granularity"))

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.request = kwargs.pop('request')


        #self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Div(
                Div(
                    Div(
                        'title',
                        'description',
                        css_class="span3",
                    ),
                    Div(
                        'max_heroes',
                        'remote',
                        'address',
                        'expiration_date',
                        css_class="span3",
                    ),
                    css_class="row",
                ),
            ),
        )
        super(QuestCreateForm, self).__init__(*args, **kwargs)
        # self.fields['location_granularity'].widget = forms.HiddenInput()
        self.fields['address'].required = False
        self.fields['address'].label = _(u"Place")
        self.fields['address'].help_text = _(u"Where does this quest take place?")
        self.fields['expiration_date'].widget = forms.DateInput(attrs={'autocomplete': 'off'})


    class Meta:
        model = Quest
        fields = ('title', 'description', 'max_heroes', 'address',
                  'expiration_date', 'remote',

                  #'latitude', 'longitude', 'location_granularity'
        )



class UserProfileEdit(forms.ModelForm):
    """Basic userprofile edit form. uses crispy-forms."""
    latitude = forms.FloatField(widget=forms.HiddenInput, required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput, required=False)
    address = forms.CharField(required=False, widget=LocationWidget("id_latitude", "id_longitude", "id_location_granularity"))

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_tag = False;

        self.helper.layout = Layout(
            Fieldset(
                _('Edit your Profile'),
                Div(
                    'hero_class',
                    'about',
                    'address',
                    'receive_system_email',
                    'receive_private_email',
                    'latitude',
                    'longitude',
                    'location_granularity',
                )
            ),

        )
        super(UserProfileEdit, self).__init__(*args, **kwargs)
        self.fields['location_granularity'].widget = forms.HiddenInput()

    class Meta:
        model = UserProfile
        fields = ('about', 'hero_class',
                  'receive_system_email', 'receive_private_email',
                  'address', 'latitude', 'longitude', 'location_granularity')


class UserProfilePrivacyEdit(forms.ModelForm):
    """Special userprofile edit form for the fields containing privacy settings."""
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag=False
        self.helper.form_method = 'post'
        #self.helper.form_action = 'userprofile-privacy-settings'
        self.helper.form_class = 'form-horizontal'

        #self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Fieldset(
                _('Privacy Settings'),
                Div(
                    'public_location',
                )
            ),

        )
        super(UserProfilePrivacyEdit, self).__init__(*args, **kwargs)

    class Meta:
        model = UserProfile
        fields = ('public_location', )


class UserRegistrationForm(RegistrationFormUniqueEmail):
    """Custom Registration form with hero class and unique email."""
    username = forms.CharField(max_length=75,
        widget=forms.TextInput(attrs={'class': 'required'}),
        label=_("Username"))


class UserAuthenticationForm(AuthenticationForm):
    """Custom login form."""
    error_messages = AuthenticationForm.error_messages
    error_messages.update({'invalid_login': _("Please enter a correct e-mail address and password. "
                                "Note that both fields are case-sensitive.")})
    email = forms.CharField(label=_("E-mail"), max_length=75)

    def __init__(self, request=None, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.help_text_inline = True

        self.helper.form_class = "box"
        self.helper.form_tag=False

        if request:
            if request.is_mobile:
                self.helper.form_action = reverse('auth_login-m')
            else:
                self.helper.form_action = reverse('auth_login')

        # make sure to use the next parameter iff exists
        if request and 'next' in request.GET:
            self.helper.form_action += "?next=" + request.GET.get('next')

        super(UserAuthenticationForm, self).__init__(request, *args, **kwargs)
        del self.fields['username']
        self.fields.keyOrder.reverse()

        email = self.fields['email']
        email.label = ""
        email.widget = forms.TextInput(attrs={'placeholder':'email'})

        password = self.fields['password']
        password.label = ""
        password.widget = forms.PasswordInput(attrs={'placeholder':'password'})

    def clean_email(self):
        self.cleaned_data['username'] = self.cleaned_data['email']
