import autocomplete_light
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Field, Div, Fieldset, Layout
from django import forms
from django.contrib.auth.models import User
from heromessage.models import Message
from django.utils.translation import ugettext_lazy as _

class MessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(User.objects.all(),
        widget=autocomplete_light.AutocompleteWidget(
        'UserChannel', max_items=1), )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
#        self.helper.form_action = 'message-c'
        self.helper.form_class = 'form'

        self.helper.layout = Layout(
            Div(
                Div(
                    'recipient',
                    css_class="span3",
                    ),
                Div(
                    'title',
                    css_class="span3",
                    ),
                css_class="row",
            ),
            Div(
                Div(
                    'text',
                    css_class="span6",
                ),
                css_class="row",
            ),
            FormActions(
                Submit('save', 'Send', css_class='btn-primary btn-large')
            ),
        )
        super(MessageForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Message
        fields = ('recipient', 'title', 'text')