from collections import defaultdict
from datetime import datetime
import logging
from django.conf import settings
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models, connection
from django.core.mail import send_mail

# Create your models here.
from django.template import Context, TemplateDoesNotExist, Template
from django.template.loader import get_template, render_to_string
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from registration.signals import user_activated
from herobase.models import Quest, Adventure, get_system_user
from heromessage.models import Message

NOTIFICATION_TYPES = {}
logger = logging.getLogger(__name__)


class NotificationTypeMetaClass(type):
    def __new__(cls, name, bases, attrs):
        new_type = super(NotificationTypeMetaClass, cls).__new__(cls, name, bases, attrs)
        if name == 'NotificationTypeBase':
            return new_type
        if not hasattr(new_type, 'type_id'):
            raise ImproperlyConfigured("Notification types need a type_id in %s" % name)
        if new_type.type_id in NOTIFICATION_TYPES:
            raise ImproperlyConfigured("Notification type ids need to be unique in %s" % name)
        if not hasattr(new_type, 'target_model'):
            raise ImproperlyConfigured("Notification types need a target_model in %s" % name)
        NOTIFICATION_TYPES[new_type.type_id] = new_type
        return new_type


class NotificationTypeBase(object):
    __metaclass__ = NotificationTypeMetaClass

    def __init__(self, user, target):
        Notification.create(user, target, type_id=self.type_id)
        if user.email:
            self.send_notification_mail(user, target)

    @classmethod
    def get_text(cls, notification):
        return ''

    @classmethod
    def get_image(cls, notification):
        return settings.STATIC_URL + 'heronotification/notification.png'

    def send_notification_mail(self, user, target):
        dict = {'notification': self, 'user': user, 'target': target}
        template_base = 'heronotification/mail/{0}'.format(type(self).__name__)
        try:
            subject = render_to_string(template_base + '.subject', dict).strip()
            text = render_to_string(template_base + '.txt', dict)
            user.email_user(subject, text)
        except TemplateDoesNotExist:
            logger.warning('template for {0} notification mail not found'.format(type(self).__name__))


class hero_has_applied(NotificationTypeBase):
    type_id = 1
    target_model = Adventure

    @classmethod
    def is_read(cls, notification):
        return (notification.target.accepted or notification.target.rejected
                or notification.target.canceled)

    @classmethod
    def get_text(cls, notification):
        return mark_safe(_(u'<strong>%(user)s</strong> is applying for your quest <strong>%(title)s</strong>.') % {
            'user': escape(notification.target.user.username),
            'title': escape(notification.target.quest.title),
        })

    @classmethod
    def get_image(cls, notification):
        return notification.target.user.profile.avatar_thumbnail_40

class hero_has_cancelled(NotificationTypeBase):
    type_id = 2
    target_model = Adventure


    @classmethod
    def get_text(cls, notification):
        return mark_safe(_(u'<strong>%(user)s</strong> has withdrawn his application for your quest <strong>%(title)s</strong>.') % {
            'user': escape(notification.target.user.username),
            'title': escape(notification.target.quest.title),
            })

    @classmethod
    def get_image(cls, notification):
        return notification.target.user.profile.avatar_thumbnail_40

class quest_started(NotificationTypeBase):
    type_id = 10
    target_model = Quest

    @classmethod
    def get_image(cls, notification):
        return notification.target.owner.profile.avatar_thumbnail_40

    @classmethod
    def get_text(cls, notification):
        return mark_safe(_("The quest <strong>%s</strong> has been started.") %
                         escape(notification.target.title))


class quest_waiting_for_documentation(NotificationTypeBase):
    type_id = 11
    target_model = Quest


    @classmethod
    def get_text(cls, notification):
        return mark_safe(_("The quest <strong>%s</strong> is waiting for documentation.") %
                         escape(notification.target.title))

class quest_cancelled(NotificationTypeBase):
    type_id = 12
    target_model = Quest

    @classmethod
    def get_image(cls, notification):
        return notification.target.owner.profile.avatar_thumbnail_40

    @classmethod
    def get_text(cls, notification):
        return mark_safe(_("The quest <strong>%s<strong> has been cancelled.") %
                         escape(notification.target.title))

class quest_done(NotificationTypeBase):
    type_id = 13
    target_model = Quest

    @classmethod
    def get_image(cls, notification):
        return notification.target.owner.profile.avatar_thumbnail_40

    @classmethod
    def get_text(cls, notification):
        return mark_safe(_("The quest <strong>%s</strong> has been completed.") %
                         escape(notification.target.title))


class hero_accepted(NotificationTypeBase):
    type_id = 100
    target_model = Quest

    @classmethod
    def get_image(cls, notification):
        return notification.target.owner.profile.avatar_thumbnail_40

    @classmethod
    def get_text(cls, notification):
        return mark_safe(_("You have been accepted for the quest <strong>%s.</strong>") %
                         escape(notification.target.title))


class hero_rejected(NotificationTypeBase):
    type_id = 101
    target_model = Quest

    @classmethod
    def get_image(cls, notification):
        return notification.target.owner.profile.avatar_thumbnail_40

    @classmethod
    def get_text(cls, notification):
        return mark_safe(_("Your application for the quest <strong>%s</strong> has been rejected.") %
                           escape(notification.target.title))

class message_received(NotificationTypeBase):
    type_id = 110
    target_model = Message

    @classmethod
    def get_text(cls, notification):
        return mark_safe(_("You have received a message from <strong>%s</strong>.") %
                         escape(notification.target.sender.username))

    @classmethod
    def get_image(cls, notification):
        return notification.target.sender.profile.avatar_thumbnail_40

    @classmethod
    def is_read(cls, notification):
        return notification.target.read

class welcome(NotificationTypeBase):
    type_id = 200
    target_model = User

    @classmethod
    def get_text(cls, notification):
        return _("Welcome to you are hero.")

    @classmethod
    def get_image(cls, notification):
        return notification.target.profile.avatar_thumbnail_40


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

    @classmethod
    def for_user(cls, user):
        items = cls.objects.filter(user=user).order_by('-read', '-created').select_related('content_type')
        # collect all targets
        # maintain a mapping ct -> id -> item
        ct_target_item_map = defaultdict(lambda: defaultdict(list))
        for item in items:
            ct_target_item_map[item.content_type][item.object_id].append(item)

        for content_type, target_item_map in ct_target_item_map.items():
            target_ids = target_item_map.keys()
            Model = content_type.model_class()
            if issubclass(Model, Quest):
                select_related = 'owner', 'owner__profile'
            elif issubclass(Model, Adventure):
                select_related = 'user', 'user__profile', 'quest'
            elif issubclass(Model, Message):
                select_related = 'sender', 'sender__profile'
            elif issubclass(Model, User):
                select_related = ('profile',)
            else:
                select_related = ()
            for target in Model.objects.filter(pk__in=target_ids).select_related(*select_related):
                for item in target_item_map[target.pk]:
                    item.target = target
        return items

    @property
    def image(self):
        if not self.type:
            return ''
        return self.type.get_image(self)

    @property
    def text(self):
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
        notification, created = Notification.objects.get_or_create(content_type=content_type, object_id=target.pk, type_id=type_id, user=user)
        if not created:
            notification.read = None
            notification.dismissed = None
            notification.created = now()
            notification.save()
        return notification

    @property
    def type(self):
        return NOTIFICATION_TYPES.get(self.type_id, None)

    def is_read(self):
        # FIXME: this still modifies the model
        if self.read is None and (not hasattr(self.type, 'is_read')
                                  or hasattr(self.type, 'is_read')
                                  and self.type.is_read(self)):
            self.read = now()
            self.save()
        return self.read

    def html(self):
        try:
            template = get_template('heronotification/%s.html' % self.type.__name__.lower())
        except TemplateDoesNotExist:
            template = get_template('heronotification/notification_base.html')

        rendered = mark_safe(template.render(Context({'notification': self})))
        return rendered


def welcome_new_user(sender, user, request, **kwargs):
    welcome(user, get_system_user())


user_activated.connect(welcome_new_user)
