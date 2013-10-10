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
from django.forms.models import model_to_dict

from django.utils.translation import ugettext_lazy as _

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div, Button, BaseInput
from registration.forms import RegistrationFormUniqueEmail

from herobase.models import Quest, UserProfile, AVATAR_IMAGES, Documentation
from herobase.widgets import LocationWidget
from herobase.utils import is_minimum_age

class DocumentationForm(forms.ModelForm):
    class Meta:
        model = Documentation
        fields = ('image', 'text', )


class QuestCreateForm(forms.ModelForm):
    """The Basic Quest create form. Uses django-crispy-forms (FormHelper) for 2 column bootstrap output. """
    remote = forms.ChoiceField(choices=(
        ("", "-----------"),
        (True, _(u"remotely")),
        (False, _(u"locally"))
    ), help_text=_(u"Can this quest be done remotely or only locally?"),
                               label=_(u"Remote or local"))
    # latitude = forms.FloatField(widget=forms.HiddenInput, required=False)
    # longitude = forms.FloatField(widget=forms.HiddenInput, required=False)
    # address = forms.CharField(widget=LocationWidget("id_latitude", "id_longitude", "id_location_granularity"))

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Div(
                Div(
                    Div(
                        'title',
                        'description',
                        css_class="col-md-6",
                    ),
                    Div(
                        'min_heroes',
                        'max_heroes',
                        'remote',
                        'time_effort',
                        'address',
                        'start_date',
                        'expiration_date',
                        'start_trigger',
                        'end_trigger',
                        css_class="col-md-6",
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

    def clean(self):
        cleaned_data = super(QuestCreateForm, self).clean()
        if ('start_date' in cleaned_data and cleaned_data['start_date'] and
                    'expiration_date' in cleaned_data and
                cleaned_data['expiration_date'] and not cleaned_data['start_date']
            < cleaned_data['expiration_date']):
            raise ValidationError("Das Startdatum muss vor dem Enddatum liegen")
        return cleaned_data

    class Meta:
        model = Quest
        fields = ('title', 'description', 'min_heroes', 'max_heroes', 'address',
                  'start_date', 'expiration_date', 'remote', 'time_effort',
                  'start_trigger', 'end_trigger'
                  #'latitude', 'longitude', 'location_granularity'
        )


class UserProfileEditForm(forms.ModelForm):
    """Basic userprofile edit form. uses crispy-forms."""
    # latitude = forms.FloatField(widget=forms.HiddenInput, required=False)
    # longitude = forms.FloatField(widget=forms.HiddenInput, required=False)
    # address = forms.CharField(required=False, widget=LocationWidget("id_latitude", "id_longitude", "id_location_granularity"))
    image = forms.ChoiceField(choices=[('', '------')] + UserProfile.avatar_choices(),
                              required=False)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Fieldset(
                _('Edit your Profile'),
                Div(
                    Div(
                        'about',
                        # 'address',
                        # 'receive_system_email',
                        # 'receive_private_email',
                        # 'latitude',
                        # 'longitude',
                        # 'location_granularity',
                        css_class="col-md-6",
                    ),
                    Div(
                        'sex',
                        'team',
                        css_class="col-md-6",
                    ),
                    css_class="row",
                ),
                Div(
                    'image',
                    'uploaded_image',
                ),
            ),
        )
        super(UserProfileEditForm, self).__init__(*args, **kwargs)
        # self.fields['location_granularity'].widget = forms.HiddenInput()

    # This method prevents us from overwriting the image field if it's empty.
    def clean(self):
        cleaned_data = super(UserProfileEditForm, self).clean()
        if cleaned_data['image'] == "":
            cleaned_data['image'] = model_to_dict(self.instance).get('image')
        return cleaned_data

    class Meta:
        model = UserProfile
        fields = ('about', 'image', 'sex', 'team', 'uploaded_image',
                  # 'receive_system_email', 'receive_private_email',
                  # 'address', 'latitude', 'longitude', 'location_granularity'
        )


class UserProfilePrivacyForm(forms.ModelForm):
    """Special userprofile edit form for the fields containing privacy settings."""

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_method = 'post'
        #self.helper.form_action = 'userprofile_privacy_settings'
        self.helper.form_class = 'form-horizontal'

        # self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Fieldset(
                _('Privacy Settings'),
                Div(
                    'public_location',
                )
            ),

        )
        super(UserProfilePrivacyForm, self).__init__(*args, **kwargs)

    class Meta:
        model = UserProfile
        fields = ('public_location', )


class UserAuthenticationForm(AuthenticationForm):
    """Custom login form."""
    error_messages = AuthenticationForm.error_messages
    error_messages.update({'invalid_login': _("Please enter a correct e-mail address and password. "
                                              "Note that both fields are case-sensitive.")})
    email = forms.CharField(label=_("E-mail"), max_length=75)
    next = forms.CharField(widget=forms.HiddenInput(), initial="/")

    def __init__(self, request=None, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.help_text_inline = True

        self.helper.form_action = 'auth_login'

        super(UserAuthenticationForm, self).__init__(request, *args, **kwargs)

        # make sure to use the next parameter if exists
        # request is only given when no POST data is submited
        if request and hasattr(request, 'GET'):
            next = request.GET.get('next', '/')
            if next == "":
                next = "/"
            self.fields['next'].initial = next # put next in POST data

        del self.fields['username']
        self.fields.keyOrder.reverse()

        email = self.fields['email']
        email.label = ""
        email.widget = forms.TextInput(
            attrs={'placeholder': 'Identität', 'autocapitalize': 'off', 'autocorrect': 'off'})

        password = self.fields['password']
        password.label = ""
        password.widget = forms.PasswordInput(attrs={'placeholder': 'Kennung'})

        self.helper.add_input(Submit('submit', 'Log in'))

    def clean_email(self):
        self.cleaned_data['username'] = self.cleaned_data['email']


class DateOfBirthRegistrationForm(RegistrationFormUniqueEmail):
    username = forms.CharField(
        max_length=75,
        widget=forms.TextInput(attrs={'class': 'required'}),
        label=_("Username")
    )
    date_of_birth = forms.DateField(label=_("Date of birth"))
