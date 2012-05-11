# -*- coding: utf-8 -*-
from django.forms.models import ModelForm
from herobase.models import Quest

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class QuestCreateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.add_input(Submit('submit', 'Submit'))
        super(QuestCreateForm, self).__init__(*args, **kwargs)
    class Meta:
        model = Quest
        fields = ('title', 'description', 'level', 'max_heroes', 'location', 'due_date', 'hero_class')