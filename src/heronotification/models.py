from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template import Context
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from herobase.models import Quest, Adventure
from heromessage.models import Message


class Notification(models.Model):
    HERO_IS_APPLYING = 10
    HERO_HAS_CANCELED= 11

    QUEST_HAS_BEEN_STARTED = 100
    QUEST_DONE = 101
    QUEST_WAITING_FOR_DOCUMENTATION = 102


    YOU_HAVE_BEEN_ACCEPTED = 1000
    YOU_HAVE_BEEN_REJECTED = 1001

    NEW_MESSAGE = 2000

    NOTIFICATION_TYPES = {
        HERO_IS_APPLYING: (Adventure, 'hero_is_applying'),
        HERO_HAS_CANCELED: (Adventure, 'hero_has_canceled'),
        QUEST_WAITING_FOR_DOCUMENTATION: (Quest, 'quest_waiting_for_documentation'),
        QUEST_DONE: (Quest, 'quest_done'),
        QUEST_HAS_BEEN_STARTED: (Quest, 'quest_has_been_started'),
        YOU_HAVE_BEEN_ACCEPTED: (Quest, 'you_have_been_accepted'),
        YOU_HAVE_BEEN_REJECTED: (Quest, 'you_have_been_rejected'),
        NEW_MESSAGE: (Message, 'new_message'),
        }

    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()

    target = generic.GenericForeignKey()
    type = models.IntegerField(choices=((key, value[1]) for key, value in NOTIFICATION_TYPES.items()))

    created = models.DateTimeField(auto_now_add=True)
    read = models.DateTimeField(blank=True, null=True)
    dismissed = models.DateTimeField(blank=True, null=True)

    @classmethod
    def create(cls, target, type):
        if not type in cls.NOTIFICATION_TYPES:
            raise ValueError("No such notification type.")

        class_, name = cls.NOTIFICATION_TYPES[type]
        if not isinstance(target, class_):
            raise ValueError("Not a valid target instance for that notification type")

        return Notification.objects.get_or_create(target=target, type=type)

    def render(self):
        template = get_template('heronotification/%s.html' % self.NOTIFICATION_TYPES[self.type][1])
        return mark_safe(template.render(Context({'notification': self})))

@receiver(pre_save, sender=Adventure)
def hero_is_applying(sender, instance=None, **kwargs):
    if instance and not instance.pk:
        Notification.create(instance, Notification.HERO_IS_APPLYING)

@receiver(pre_save, sender=Adventure)
def hero_has_cancelled(sender, instance=None, **kwargs):
    if instance and instance.pk and instance.canceled:
        if Adventure.objects.get(pk=instance.pk, canceled=False).exists():
            Notification.create(instance, Notification.HERO_HAS_CANCELED)

        