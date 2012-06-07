from django.contrib.auth.models import User
from django.db import models

# Create your models here.
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

    def __unicode__(self):
        return '%s -> %s: %s' % (self.sender.username, self.recipient.username, self.title)