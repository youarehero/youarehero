# -"- coding:utf-8 -"-
"""
This module provides all the basic Quest related models for You are HERO.
The most important are Quest, Userprofile (represents a hero) and Adventure.
This module also contains the ActionMixin, which provides basic logic for model actions.
The model actions connect state logic to the models.
"""
from datetime import datetime, timedelta
from random import randint
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

import os
import textwrap

from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.db.models.query import QuerySet
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from easy_thumbnails.files import get_thumbnailer
from south.modelsinspector import add_introspection_rules

from heromessage.models import Message

# The classes a User can choose from. (Hero classes)
CLASS_CHOICES =  (
    (5, "Scientist"),
    (1, 'Gadgeteer'),
    (2, 'Diplomat'),
    (3, 'Action'),
    (4, 'Protective'))


class Like(models.Model):
    user = models.ForeignKey(User)
    quest = models.ForeignKey('Quest')


class LocationMixin(models.Model):
    latitude = models.FloatField(null=True, db_index=True, blank=True)
    longitude = models.FloatField(null=True, db_index=True, blank=True)
    address = models.CharField(max_length=255, blank=True, default='')

    LOCATION_GRANULARITY_NONE = 0
    LOCATION_GRANULARITY_GPS = 1
    LOCATION_GRANULARITY_ADDRESS = 2
    LOCATION_GRANULARITY_DISTRICT = 3
    LOCATION_GRANULARITY_CITY = 4
    LOCATION_GRANULARITY_UNKNOWN = 5

    location_granularity = models.IntegerField(default=LOCATION_GRANULARITY_NONE,
        choices=((LOCATION_GRANULARITY_NONE, _(u"no location")),
                 (LOCATION_GRANULARITY_GPS, _(u"GPS")),
                 (LOCATION_GRANULARITY_ADDRESS, _(u"address")),
                 (LOCATION_GRANULARITY_DISTRICT, _(u"district")),
                 (LOCATION_GRANULARITY_CITY, _(u"city")),
                 (LOCATION_GRANULARITY_UNKNOWN, _(u"unknown")),
        ))

    @property
    def has_location(self):
        return not self.location_granularity == self.LOCATION_GRANULARITY_NONE

    def save(self, force_insert=False, force_update=False, using=None):
        if (self.latitude and self.longitude
            and self.location_granularity == self.LOCATION_GRANULARITY_NONE):
            self.location_granularity = self.LOCATION_GRANULARITY_UNKNOWN
        return super(LocationMixin, self).save(force_insert, force_update,
            using)


    class Meta:
        abstract = True


class AdventureQuerySet(QuerySet):
    def applying(self):
        """Show only adventures that have not been canceled."""
        return self.filter(canceled=False, accepted=False, rejected=False)


class AdventureManager(models.Manager):
    """Custom Object Manager for Adventures, excluding canceled ones."""
    def get_query_set(self):
        return AdventureQuerySet(model=self.model, using=self._db)
    def applying(self):
        """Show only adventures that have not been canceled."""
        return self.get_query_set().applying()


class Adventure(models.Model):
    objects = AdventureManager()

    user = models.ForeignKey(User, related_name='adventures')
    quest = models.ForeignKey('Quest', related_name='adventures')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    accepted = models.BooleanField(default=False)
    accepted_time = models.DateTimeField(null=True, blank=True, editable=False)

    rejected = models.BooleanField(default=False)
    rejected_time = models.DateTimeField(null=True, blank=True, editable=False)

    canceled = models.BooleanField(default=False)
    canceled_time = models.DateTimeField(null=True, blank=True, editable=False)

    done = models.BooleanField(default=False)
    done_time = models.DateTimeField(null=True, blank=True, editable=False)

    @property
    def applying(self):
        return not self.rejected and not self.accepted and not self.canceled

    def save(self, force_insert=False, force_update=False, using=None):
        if self.accepted and not self.accepted_time:
            self.accepted_time = now()
        if self.rejected and not self.rejected_time:
            self.rejected_time = now()
        if self.done and not self.done_time:
            self.done_time = now()
        if self.canceled and not self.canceled_time:
            self.canceled_time = now()
        return super(Adventure, self).save(force_insert, force_update, using)


    def __unicode__(self):
        return '%s - %s' % (self.quest.title, self.user.username)

    def get_absolute_url(self):
        return self.quest.get_absolute_url()


    def get_state_display(self):
        if self.canceled:
            return _(u"cancelled")
        elif self.accepted:
            return _(u"accepted")
        elif self.rejected:
            return _(u"rejected")
        else:
            return _(u"pending")


class QuestQuerySet(QuerySet):
    def open(self):
        return self.filter(open=True).filter(expiration_date__gt=now())


class QuestManager(models.Manager):
    """Custom Quest Object Manager, for active and inactive `Quest` objects"""
    def get_query_set(self):
        return QuestQuerySet(model=self.model, using=self._db)
    def open(self):
        return self.get_query_set().open()


class Quest(LocationMixin, models.Model):
    """A quest, owned by a user."""
    objects = QuestManager()

    owner = models.ForeignKey(User, related_name='created_quests')
    title = models.CharField(max_length=255, verbose_name=_(u"Title"))
    description = models.TextField(verbose_name=_(u"Description"),
                                   help_text=_(u"A short description of what "
                                               u"this quest is about."))

    expiration_date = models.DateTimeField(default=lambda: now() + timedelta(days=30),
                                           verbose_name=_(u"Expiration date"),
                                           help_text=_(u"Until which date will "
                                                       u"this quest be visible?"))

    heroes = models.ManyToManyField(User, through=Adventure, related_name='quests')

    remote = models.BooleanField(default=True, verbose_name=_(u"Can be done remotely"),
                                 help_text=_(u"Can this quest be done remotely or only locally?"))

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    max_heroes = models.PositiveIntegerField(default=1,
                                             validators=[MinValueValidator(1)],
                                             verbose_name=_(u"Number of heroes"),
                                             help_text=_(u"How many heroes "
                                                         u"can participate in "
                                                         u"this Quest?"))

    # still needs heroes
    open = models.BooleanField(default=True)

    # owner has canceled the quest
    canceled = models.BooleanField(default=False)
    canceled_time = models.DateTimeField(null=True, blank=True, editable=False)

    # owner has marked quest as done
    done = models.BooleanField(default=False)
    done_time = models.DateTimeField(null=True, blank=True, editable=False)

    # owner has started the quest
    started = models.BooleanField(default=False)
    started_time = models.DateTimeField(null=True, blank=True, editable=False)

    time_effort = models.IntegerField(null=True, choices=(
        (1, _(u"Low")),
        (2, _(u"Medium")),
        (3, _(u"Hight")),
    ))

    @property
    def has_expired(self):
        return self.expiration_date < now()

    @property
    def can_accept_all(self):
        return self.open and self.adventures.filter(accepted=False, rejected=False, canceled=False).exists()

    @property
    def can_start(self):
        return (self.open and not self.adventures.filter(accepted=False, rejected=False, canceled=False).exists()
                and self.adventures.filter(accepted=True, canceled=False).exists())

    def save(self, force_insert=False, force_update=False, using=None):
        self.open = not self.pk or (not self.done and not self.canceled and not self.started)

        if self.canceled and not self.canceled_time:
            self.canceled_time = now()
        if self.started and not self.started_time:
            self.started_time = now()
        if self.done and not self.done_time:
            self.done_time = now()

        return super(Quest, self).save(force_insert, force_update, using)

    def get_absolute_url(self):
        """Get the url for this quests detail page."""
        return reverse("quest_detail", args=(self.pk,))


    def get_state_display(self):
        if self.canceled:
            return "abgebrochen"
        elif self.done:
            return "erledigt"
        elif self.started:
            return "hat begonnen"
        elif self.expiration_date < now():
            return "abgelaufen"
        else:
            return "offen"

    def __unicode__(self):
        """String representation"""
        return self.title


class Comment(models.Model):
    author = models.ForeignKey(User, related_name='comments')
    quest = models.ForeignKey(Quest, related_name='comments')

    created = models.DateTimeField(auto_now_add=True)

    text = models.TextField()

    class Meta:
        ordering = ('-created', )


class AvatarImageMixin(object):
    avatar_storage = FileSystemStorage(location=os.path.join(settings.PROJECT_ROOT, 'assets/'))

    def avatar(self):
        """Return a String, containing a path to a thumbnail-image 270x270."""
        return self._avatar_thumbnail((270, 270))

    @property
    def avatar_thumbnail(self):
        """Return a String, containing a path to a thumbnail-image 40x40."""
        return self._avatar_thumbnail((50, 50))

    @property
    def avatar_thumbnail_40(self):
        """Return a String, containing a path to a thumbnail-image 40x40."""
        return self._avatar_thumbnail((40, 40))

    @property
    def avatar_thumbnail_80(self):
        """Return a String, containing a path to a thumbnail-image 40x40."""
        return self._avatar_thumbnail((80, 80))
    @property
    def avatar_thumbnail_110(self):
        """Return a String, containing a path to a thumbnail-image 40x40."""
        return self._avatar_thumbnail((110, 110))

    @property
    def avatar_thumbnail_30(self):
        """Return a String, containing a path to a thumbnail-image 40x40."""
        return self._avatar_thumbnail((30, 30))

    def _avatar_thumbnail(self, size):
        """Return a String, containing a path to a thumbnail-image 40x40."""
        file_name = "default.png"
        image = os.path.join('avatar/', file_name)
        thumbnailer = get_thumbnailer(self.avatar_storage, image)
        thumbnail = thumbnailer.get_thumbnail({'size': size, 'quality': 90})
        return os.path.join(settings.MEDIA_URL, thumbnail.url)


class UserProfile(LocationMixin, models.Model, AvatarImageMixin):
    """This model extends a django user with additional hero information."""
    add_introspection_rules([], ["^herobase\.fields\.LocationField"])

    objects = models.Manager()

    user = models.OneToOneField(User, related_name='profile')
    experience = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=255) # TODO : placeholder
    hero_class = models.IntegerField(choices=CLASS_CHOICES, blank=True,
        null=True)

    keep_email_after_gpn = models.DateTimeField(blank=True, null=True,
        editable=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    public_location = models.BooleanField(default=False,
        verbose_name=_("Location is public"),
        help_text=_("Enable this if you want to share "
                    "your location with other Heroes."))

    about = models.TextField(blank=True, default='',
        help_text=_('Tell other heroes who you are.'))

    receive_system_email = models.BooleanField(default=False,
        verbose_name=_("E-Mail on quest changes"),
        help_text=_("Enable this if you want to receive an email notification "
                    "when one of your quests needs attention."))

    receive_private_email = models.BooleanField(default=False,
        verbose_name=_("E-Mail on private message"),
        help_text=_("Enable this if you want to receive an email notification "
                    "when someone sends you a private message."))

    def quests_done(self):
        return self.user.adventures.filter(quest__done=True, accepted=True, canceled=False).count()

    def quests_created(self):
        return self.user.created_quests.count()

    @property
    def level(self):
        """Calculate the user's level based on her experience"""
        return int(self.experience / 1000) + 1 # TODO: correct formula

    def relative_level_experience(self):
        """Calculates percentage of XP for current level."""
        return (self.experience % 1000) / 10 # TODO: correct formula

    @property
    def unread_messages_count(self):
        """Return number of unread messages."""
        return Message.objects.filter(recipient=self.user,read__isnull=True,
            recipient_deleted__isnull=True).count()

    @property
    def rank(self):
        return list(User.objects.select_related().order_by( 'experience', 'username' )).index(self.user) + 1

    def __unicode__(self):
        return self.user.username

    def get_global_relative_leaderboard(self, top_count=3, neighbourhood_size=5):
        """
        Returns a location based relative leaderboard for this userprofile
        containing the top rated users as well as those close in rank.

        :param top_count: The top n users to include
        :param neighbourhood_size: The number of users with similar ranks to be included
        """
        # FIXME: we need to add the  ranks to the qs
        raise NotImplementedError("Need to re-implement as per docstring")

    def get_local_relative_leaderboard(self, top_count=3, neighbourhood_size=5):
        """
        Returns a relative leaderboard for this userprofile containing the top
        rated users as well as those close in rank.

        :param top_count: The top n users to include
        :param neighbourhood_size: The number of users with similar ranks to be included
        """
        if not self.has_location:
            return []
        # FIXME: we need to add the  ranks to the qs
        raise NotImplementedError("Need to re-implement as per docstring")



def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile on user account creation."""
    if created:
        try:
            UserProfile.objects.get_or_create(user=instance)
        except:
            pass
post_save.connect(create_user_profile, sender=User)




class AbuseReport(models.Model):
    TYPE_NOT_SET = 0
    TYPE_SPAM = 1
    TYPE_ILLEGAL_CONTENT = 2
    TYPE_HATE_SPEECH = 3
    text = models.TextField(verbose_name=_("text"))
    type = models.IntegerField(default=TYPE_NOT_SET, choices=(
        (TYPE_NOT_SET, _("type not set")),
        (TYPE_SPAM, _("spam")),
        (TYPE_ILLEGAL_CONTENT, _("illegal content")),
        (TYPE_HATE_SPEECH, _("hate speech")),
        ))
    reporter = models.ForeignKey(User, related_name='reported report')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')


from registration.signals import user_activated
from django.contrib.auth import login, authenticate

def login_on_activation(sender, user, request, **kwargs):
    """Logs in the user after activation"""
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)

# Registers the function with the django-registration user_activated signal
user_activated.connect(login_on_activation)

SYSTEM_USER_NAME = "YouAreHero"

def get_system_user():
    """Return an unique system-user. Creates one if not existing."""
    user, created = User.objects.get_or_create(username=SYSTEM_USER_NAME)
    return user

def get_dummy_user():
    return UserProfile(user=User(username="dummy"))


def getTopUser():
    all=list(User.objects.select_related().order_by( 'experience', 'username' ))
    top={}
    for place in range(0,10) :
        top.append(all[place])

    return top