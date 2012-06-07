# -*- coding: utf-8 -*-
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms import forms
from django.forms.fields import CharField, IntegerField, EmailField
from django.forms.models import ModelForm
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div
from registration.forms import RegistrationFormUniqueEmail

from herobase.models import Quest, UserProfile
from herobase.widgets import LocationWidget


class QuestCreateForm(ModelForm):
    experience = IntegerField(initial=100)
    level = IntegerField(initial=1)
    location = CharField(initial="GPN")
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
       # self.helper.form_action = 'quest-create'
       # self.helper.form_class = 'form-horizontal'
        self.request = kwargs.pop('request')

        #self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Fieldset(
                'Create a Quest',
                Div(
                    Div(
                        'title',
                        'hero_class',
                        'description',
                        css_class="span3",
                    ),
                    Div(
                        'level',
                        'experience',
                        'max_heroes',
                        'auto_accept',
                        'location',
                        'due_date',
                        css_class="span3",
                    ),
                    css_class="row",
                ),
            ),
            FormActions(
                Submit('save', 'Save', css_class='btn-large')
            ),
        )
        super(QuestCreateForm, self).__init__(*args, **kwargs)


    def clean_level(self):
        data = self.cleaned_data['level']
        if self.request.user.get_profile().level < int(data):
            raise ValidationError("Your level is not high enough for this quest level!")
        return data

    def clean(self):
        data = super(QuestCreateForm, self).clean()
        if ('experience' in data and 'level' in data and
            int(data['experience']) > int(data['level']) * 100): # TODO experience formula
            self._errors['experience'] = self._errors.get('experience', ErrorList())
            self._errors['experience'].append(_(u'Experience to high for level.'))
            del data['experience']
        return data

    class Meta:
        model = Quest
        fields = ('title', 'description', 'max_heroes', 'location', 'due_date', 'hero_class', 'level' ,'experience', 'auto_accept')


class UserProfileEdit(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        #self.helper.form_action = 'user-edit'
        self.helper.form_class = 'form-horizontal'

        #self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Fieldset(
                _('Edit your Profile'),
                Div(
                    'hero_class',
                    'location',
                    'geolocation',
                )
            ),
            FormActions(
                Submit('save', 'Save', css_class='btn-large')
            ),
        )
        super(UserProfileEdit, self).__init__(*args, **kwargs)

    class Meta:
        model = UserProfile
        fields = ('location', 'hero_class', 'geolocation')
        widgets = {
            'title': LocationWidget,
        }

class UserProfilePrivacyEdit(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
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
            FormActions(
                Submit('save', 'Save', css_class='btn-large')
            ),
        )
        super(UserProfilePrivacyEdit, self).__init__(*args, **kwargs)

    class Meta:
        model = UserProfile
        fields = ('public_location', )


class UserRegistrationForm(RegistrationFormUniqueEmail):
    username = CharField(max_length=75,
        widget=forms.TextInput(attrs={'class': 'required'}),
        label=_("Username"))

class UserAuthenticationForm(AuthenticationForm):
    error_messages = AuthenticationForm.error_messages
    error_messages.update({'invalid_login': _("Please enter a correct e-mail address and password. "
                                "Note that both fields are case-sensitive.")})
    email = EmailField(label=_("E-mail"), max_length=75)
    def __init__(self, request=None, *args, **kwargs):
        super(UserAuthenticationForm, self).__init__(request, *args, **kwargs)
        del self.fields['username']
        self.fields.keyOrder.reverse()

    def clean_email(self):
        self.cleaned_data['username'] = self.cleaned_data['email']