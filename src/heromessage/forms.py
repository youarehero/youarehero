import autocomplete_light
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Field, Div, Fieldset, Layout
from django import forms
from django.contrib.auth.models import User
from heromessage.models import Message
from django.utils.translation import ugettext_lazy as _
from herobase.models import UserProfile

class MessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(
        User.objects.all(),
        widget=autocomplete_light.ChoiceWidget('UserAutocomplete'),
        label=_(u'Neue Nachricht an'),
    )
    text = forms.CharField(
        widget=forms.Textarea(),
        label='',
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag=False
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'recipient',
            'title',
            Field('text', css_class="no-label"),
        )
        super(MessageForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Message
        fields = ('recipient', 'title', 'text')


class TeamMessageForm(forms.Form):
    team = forms.ChoiceField(
        label = _("Recipient Team"),
        choices = [(entry['team'], entry['team']) for entry in UserProfile.objects.values('team').exclude(team="").distinct()],
        widget=autocomplete_light.ChoiceWidget('TeamAutocomplete')
    )

    title = forms.CharField(max_length=255, label=_("Subject"))
    text = forms.CharField(label=_("Message"), widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag=False
        self.helper.form_method = 'post'
#        self.helper.form_action = 'message-c'
        self.helper.form_class = 'form box'

        self.helper.layout = Layout(
            Div(
                Div(
                    'team',
                    css_class="col-md-6",
                    ),
                Div(
                    'title',
                    css_class="col-md-6",
                    ),
                css_class="row",
            ),
            Div(
                Div(
                    Field('text', css_class="col-md-12"),
                    css_class="col-md-12",
                ),
                css_class="row",
            ),

        )
        super(TeamMessageForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ('team', 'title', 'text')


class QuestMessageForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag=False
        self.helper.form_method = 'post'
#        self.helper.form_action = 'message-c'
        self.helper.form_class = 'form box'

        self.helper.layout = Layout(
            Div(
                Div(
                    'title',
                    css_class="col-md-12",
                    ),
                css_class="row",
            ),
            Div(
                Div(
                    Field('text', css_class="col-md-12"),
                    css_class="col-md-12",
                ),
                css_class="row",
            ),

        )
        super(QuestMessageForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Message
        fields = ('title', 'text')
