from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models

# Create your models here.
from django.template import Context, TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from herobase.models import Quest, Adventure

NOTIFICATION_TYPES = {}

class NotificationTypeMetaClass(type):
    def __new__(cls, name, bases, attrs):
        type = super(NotificationTypeMetaClass, cls).__new__(cls, name, bases, attrs)
        if name == 'NotificationTypeBase':
            return type
        if not hasattr(type, 'id'):
            raise ImproperlyConfigured("Notification types need an id in %s" % name)
        if type.id in NOTIFICATION_TYPES:
            raise ImproperlyConfigured("Notification type ids need to be unique in %s" % name)
        if not hasattr(type, 'target_model'):
            raise ImproperlyConfigured("Notification types need a target_model in %s" % name)
        NOTIFICATION_TYPES[type.id] = type
        return type


class NotificationTypeBase(object):
    __metaclass__ = NotificationTypeMetaClass

    def __init__(self, user, target):
        Notification.create(user, target, type_id=self.id)

    @classmethod
    def get_text(cls, notification):
        return ''


class hero_has_applied(NotificationTypeBase):
    id = 1
    target_model = Adventure

    @classmethod
    def is_read(cls, notification):
        return (notification.target.accepted or notification.target.rejected
                or notification.target.canceled)

    @classmethod
    def get_text(cls, notification):
        return mark_safe("<strong>%s</strong> is applying for "
                         "your quest <strong>%s</strong>." %
                         (notification.target.user.username,
                          notification.target.quest.title))


class hero_has_cancelled(NotificationTypeBase):
    id = 2
    target_model = Adventure

    @classmethod
    def get_text(cls, notification):
        return mark_safe("<strong>%s</strong> has cancelled his application "
                         "for your quest <strong>%s</strong>." %
                         (notification.target.user.username,
                          notification.target.quest.title))


class quest_started(NotificationTypeBase):
    id = 10
    target_model = Quest

    @classmethod
    def get_text(cls, notification):
        return mark_safe("The quest <strong>%s</strong> has been started." %
                         notification.target.title)


class quest_waiting_for_documentation(NotificationTypeBase):
    id = 11
    target_model = Quest

    @classmethod
    def get_text(cls, notification):
        return mark_safe("The quest <strong>%s</strong> is waiting for documentation." %
                         notification.target.title)

class quest_cancelled(NotificationTypeBase):
    id = 12
    target_model = Quest

    @classmethod
    def get_text(cls, notification):
        return mark_safe("The quest <strong>%s</strong> has been cancelled." %
                         notification.target.title)

class quest_done(NotificationTypeBase):
    id = 13
    target_model = Quest

    @classmethod
    def get_text(cls, notification):
        return mark_safe("The quest <strong>%s</strong> has been completed." %
                         notification.target.title)


class hero_accepted(NotificationTypeBase):
    id = 100
    target_model = Quest

    @classmethod
    def get_text(cls, notification):
        return mark_safe("You have been accepted for the quest<strong>%s</strong>." %
                         notification.target.title)


class hero_rejected(NotificationTypeBase):
    id = 101
    target_model = Quest

    @classmethod
    def get_text(cls, notification):
        return mark_safe("Your application for the quest<strong>%s</strong> "
                         "has been rejected." % notification.target.title)


class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()

    target = generic.GenericForeignKey()
    type_id = models.IntegerField(choices=((key, value.__name__)
        for key, value in NOTIFICATION_TYPES.items()))

    created = models.DateTimeField(auto_now_add=True)
    read = models.DateTimeField(blank=True, null=True)
    dismissed = models.DateTimeField(blank=True, null=True)

    def is_dismissible(self):
        return True

    def get_text(self):
        if not self.type:
            return 'untyped notification'
        return self.type.get_text(self)

    @classmethod
    def create(cls, user, target, type_id):
        if not type_id in NOTIFICATION_TYPES:
            raise ValueError("No such notification type.")

        notification_type = NOTIFICATION_TYPES[type_id]

        if not isinstance(target, notification_type.target_model):
            raise ValueError("Not a valid target instance for that notification type")

        content_type = ContentType.objects.get_for_model(target)
        return Notification.objects.get_or_create(content_type=content_type, object_id=target.pk, type_id=type_id, user=user)

    @property
    def type(self):
        return NOTIFICATION_TYPES.get(self.type_id, None)

    def is_read(self):
        # FIXME: this still modifies the model
        if self.read is None and hasattr(self.type, 'is_read') and self.type.is_read(self):
            self.read = datetime.now()
            self.save()
        return self.read

    def html(self):
        try:
            template = get_template('heronotification/%s.html' % self.type.__name__.lower())
        except TemplateDoesNotExist:
            template = get_template('heronotification/notification_base.html')

        rendered = mark_safe(template.render(Context({'notification': self})))
        return rendered


# we have a notification with a generic foreign key
# we have different kinds of notifications for a single target
# combinations of target content type and kind of notification have different is_read methods
# we want to be able to send notifications from anywhere like so:
# notification.send(user, quest, QUE

#
# notification.send(request.user, quest, notification.QUEST_STARTED)
# notify.quest_started(user, quest)
#
