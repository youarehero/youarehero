# -*- coding: utf-8 -*-
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div
from django.utils.translation import ugettext as _
from django import forms
import logging
from .models import Organization

logger = logging.getLogger(__name__)


class OrganizationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Fieldset(
                _('Edit your Profile'),
                Div('description', css_class='col-md-6'),
                Div('image', css_class='col-md-6'),
            ),
        )
        super(OrganizationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Organization
        fields = []