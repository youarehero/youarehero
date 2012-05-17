# -*- coding: utf-8 -*-
from crispy_forms.bootstrap import FormActions
from django.conf.urls import url
from django.forms.models import ModelForm
from herobase.models import Quest

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div


class QuestCreateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'quest-create'
        self.helper.form_class = 'form-horizontal'

        #self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Fieldset(
                'Create a Quest',
                Div(
                    Div(
                    'title',
                    'description',

                        css_class="span6",
                    ), Div(
                    'hero_class',
                    'max_heroes',
                    'location',
                    'due_date',
                        css_class="span6",
                    ),
                    css_class="row",
                ),
            ),
            FormActions(
                Submit('save', 'Save', css_class='btn-primary btn-large')
            ),
        )
        super(QuestCreateForm, self).__init__(*args, **kwargs)
    class Meta:
        model = Quest
        fields = ('title', 'description', 'max_heroes', 'location', 'due_date', 'hero_class')