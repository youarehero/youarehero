# -*- coding: utf-8 -*-
import logging
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from models import UserSelectionProfile, SKILLS
from django.utils.translation import ugettext as _


logger = logging.getLogger(__name__)

def bool_check_test(value):
    return bool(value)

class FloatCheckboxInput(forms.CheckboxInput):
    def __init__(self, attrs=None, check_test=bool_check_test):

        super(FloatCheckboxInput, self).__init__(attrs, check_test)

    def value_from_datadict(self, data, files, name):
        if name not in data:
        # A missing value means False because HTML form submission does not
        # send results for unselected checkboxes.
            return 0.0
        value = data.get(name)
        if value.lower() == 'false':
            return 0.0
        return 1.0

class UserSkillEditForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserSkillEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        #self.helper.form_action = 'user-edit'
        self.helper.form_class = 'form-horizontal'

        self.helper.add_input(Submit('submit', _('Submit')))

    class Meta:
        model = UserSelectionProfile
        fields = tuple(SKILLS)
        widgets = dict((field, FloatCheckboxInput) for field in fields)


