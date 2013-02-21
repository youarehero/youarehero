from datetime import timedelta
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.utils.timezone import now
from django.utils.translation import ugettext as t
from django.utils.translation import ugettext_lazy as _
# Create your models here.
import logging

logger = logging.getLogger('youarehero.heromessage')

class Message(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("title"))
    text = models.TextField(verbose_name=_("text"))

    sent = models.DateTimeField(auto_now_add=True)
    read = models.DateTimeField(blank=True, null=True)

    recipient_archived = models.DateTimeField(blank=True, null=True)
    recipient_deleted = models.DateTimeField(blank=True, null=True)

    sender_archived = models.DateTimeField(blank=True, null=True)
    sender_deleted = models.DateTimeField(blank=True, null=True)

    in_reply_to = models.ForeignKey('self', null=True, blank=True, related_name='+')

    recipient = models.ForeignKey(User, related_name='sent_messages', verbose_name=_("recipient"))
    sender = models.ForeignKey(User, related_name='received_messages', verbose_name=_("sender"))

    class Meta:
        ordering = ['-sent']

    @property
    def is_relatively_new(self):
        return not self.read or (now() - self.read) < timedelta(minutes=5)

    @property
    def is_read(self):
        return self.read is not None

    def __unicode__(self):
        return '%s' % self.title

    @classmethod
    def send(cls, sender, recipient, title, text):
        return cls.objects.create(
            recipient=recipient,
            sender=sender,
            title=title,
            text=text
        )

    def get_absolute_url(self):
        return reverse('message_list_in')

def send_email_for_message(message):
    send_mail(t('You are Hero - new Message - %s') % message.title,
        message.text,
        'noreply@youarehero.net',
        [message.recipient.email],
        fail_silently=True
    )

def send_mail_on_message_save(sender, **kwargs):
    from herobase.models import get_system_user
    if 'instance' in kwargs and kwargs.get('created', False):
        message = kwargs['instance']
        recipient = message.recipient
        if message.sender == get_system_user() and recipient.get_profile().receive_system_email:
            send_email_for_message(message)
        elif message.sender != get_system_user() and recipient.get_profile().receive_private_email:
            send_email_for_message(message)

post_save.connect(send_mail_on_message_save, Message, dispatch_uid="heromessage.models")