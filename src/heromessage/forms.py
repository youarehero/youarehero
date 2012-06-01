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
        self.helper.form_action = 'message-list'
        self.helper.form_class = 'well form-horizontal'

        self.helper.layout = Layout(
            Fieldset(
                _('Send a new Message'),
                Div(
                    Field(
                        'recipient',
                        #HTML('<input type="text" data-provide="typeahead">'),
                    ),
                    'title',
                    'text',
                )
            ),
            FormActions(
                Submit('save', 'Send', css_class='btn-primary btn-large')
            ),
        )
        super(MessageForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Message
        fields = ('recipient', 'title', 'text')