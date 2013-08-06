# -*- coding: utf-8 -*-
from django import forms
import logging
from .models import Organization

logger = logging.getLogger(__name__)


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ('description', )