from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Fieldset, Layout, Div, HTML, Field
from django.contrib.auth.models import User
from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _

# Create your models here.
from django.forms.models import ModelForm
import logging
logger = logging.getLogger('youarehero.heromessage')

class Message(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()

    sent = models.DateTimeField(auto_now_add=True)
    read = models.DateTimeField(blank=True, null=True)

    recipient_archived = models.DateTimeField(blank=True, null=True)
    recipient_deleted = models.DateTimeField(blank=True, null=True)

    sender_archived = models.DateTimeField(blank=True, null=True)
    sender_deleted = models.DateTimeField(blank=True, null=True)

    recipient = models.ForeignKey(User, related_name='sent_messages')
    sender = models.ForeignKey(User, related_name='received_messages')

    @property
    def is_read(self):
        return self.read is not None

class MessageForm(ModelForm):

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
                        HTML('<input type="text" data-provide="typeahead">'),
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