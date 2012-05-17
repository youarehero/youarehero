from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Message(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()

    sent = models.DateTimeField(auto_created=True)
    read = models.DateTimeField(blank=True, null=True)

    recipient_archived = models.DateTimeField(blank=True, null=True)
    recipient_deleted = models.DateTimeField(blank=True, null=True)

    sender_archived = models.DateTimeField(blank=True, null=True)
    sender_deleted = models.DateTimeField(blank=True, null=True)

    recipient = models.ForeignKey(User, related_name='sent_messages')
    sender = models.ForeignKey(User, related_name='received_messages')