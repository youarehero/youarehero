# -"- coding:utf-8 -"-
"""
This module provides all the basic Quest related models for You are HERO.
The most important are Quest, Userprofile (represents a hero) and Adventure.
This module also contains the ActionMixin, which provides basic logic for model actions.
The model actions connect state logic to the models.
"""
from datetime import datetime
from random import randint
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

import os
import textwrap

from django.core.files.storage import FileSystemStorage
from django.db.models.query import QuerySet
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.db import models
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


class Adventure(models.Model):

    user = models.ForeignKey(User, related_name='adventures')
    quest = models.ForeignKey('Quest')
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

    def save(self, force_insert=False, force_update=False, using=None):
        if self.accepted and not self.accepted_time:
            self.accepted_time = datetime.now()
        if self.rejected and not self.rejected_time:
            self.rejected_time = datetime.now()
        if self.done and not self.done_time:
            self.done_time = datetime.now()
        if self.canceled and not self.canceled_time:
            self.canceled_time = datetime.now()
        return super(Adventure, self).save(force_insert, force_update, using)


    def __unicode__(self):
        return '%s - %s' % (self.quest.title, self.user.username)


class QuestQuerySet(QuerySet):
    def open(self):
        return self.filter(open=True)


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
    title = models.CharField(max_length=255)
    description = models.TextField()

    due_date = models.DateTimeField()

    hero_class = models.IntegerField(choices=CLASS_CHOICES, blank=True, null=True)
    heroes = models.ManyToManyField(User, through=Adventure, related_name='quests')

    remote = models.BooleanField(default=True, verbose_name=_(u"Can be done remotely"))

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    max_heroes = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    auto_accept = models.BooleanField(default=False, verbose_name=_("accept automatically"),
        help_text=_("If set heroes will be accepted automatically. "
                    "This means that you won't be able to refuse an offer."))

    experience = models.PositiveIntegerField()

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

    level = models.IntegerField(editable=False, default=1)

    def save(self, force_insert=False, force_update=False, using=None):
        self.open = not self.pk or (not self.done and not self.canceled and
                     self.adventure_set.filter(accepted=True, canceled=False).count() < self.max_heroes)

        if self.canceled and not self.canceled_time:
            self.canceled_time = datetime.now()
        if self.started and not self.started_time:
            self.started_time = datetime.now()
        if self.done and not self.done_time:
            self.done_time = datetime.now()

        return super(Quest, self).save(force_insert, force_update, using)

    def active_heroes(self):
        """Return all heroes active on a quest. These are accepted heroes
         and heroes who claim to be done."""
        return self.heroes.filter(adventures__quest=self.pk,
            adventure__accepted=True)

    def accepted_heroes(self):
        """Return all accepted heroes and following states (heros who
        are done or claim so)"""
        return self.heroes.filter(adventures__quest=self.pk,
            adventures__accepted=True,
            adventures__canceled=False)

    def applying_heroes(self):
        """Return all heroes, applying for the quest."""
        return self.heroes.filter(adventures__quest=self.pk,
            adventures__canceled=False,
            adventures__rejected=False)

    def remaining_slots(self):
        """Number of heroes who may participate in the quest until maximum
         number of heroes is achieved"""
        return self.max_heroes - self.accepted_heroes().count()

    def get_absolute_url(self):
        """Get the url for this quests detail page."""
        return reverse("quest-detail", args=(self.pk,))
    def get_absolute_m_url(self):
        """Get the url for this quests detail page."""
        return reverse("m-quest-detail", args=(self.pk,))

    def __unicode__(self):
        """String representation"""
        return self.title


class AvatarImageMixin(object):
    # FIXME: this should be done by templatetags
    CLASS_AVATARS = {
        5: "scientist.jpg",
        1: 'gadgeteer.jpg',
        2: 'diplomat.jpg',
        3: 'action.jpg',
        4: 'protective.jpg'}

    avatar_storage = FileSystemStorage(location=os.path.join(settings.PROJECT_ROOT, 'assets/'))

    def avatar_thumbnails(self):
        """Return a list of avatar thumbnails 50x50"""
        return self._avatar_thumbnails((50, 50))

    def avatar_thumbnails_tiny(self):
        """Return a list of avatar thumbnails 15x15"""
        return self._avatar_thumbnails((15, 15))

    def _avatar_thumbnails(self, size):
        """Return a list of tuples (id,img_url) of avatar thumbnails."""
        thumbs = []
        for id, image_name in self.CLASS_AVATARS.items():
            image = os.path.join('avatar/', image_name)
            thumbnailer = get_thumbnailer(self.avatar_storage, image)
            thumbnail = thumbnailer.get_thumbnail({'size': size, 'quality': 90})
            thumbs.append((id, os.path.join(settings.MEDIA_URL, thumbnail.url)))
        return thumbs

    def avatar(self):
        """Return a String, containing a path to a thumbnail-image 270x270."""
        file_name = "default.png"
        if self.hero_class is not None:
            file_name = self.CLASS_AVATARS[self.hero_class]
        image = os.path.join('avatar/', file_name)
        thumbnailer = get_thumbnailer(self.avatar_storage, image)
        thumbnail = thumbnailer.get_thumbnail({'size': (270, 270),
                                               'quality': 90})
        return os.path.join(settings.MEDIA_URL, thumbnail.url)

    @property
    def avatar_thumb(self):
        """Return a String, containing a path to a thumbnail-image 40x40."""
        file_name = "default.png"
        if self.hero_class  is not None:
            file_name = self.CLASS_AVATARS[self.hero_class]
        image = os.path.join('avatar/', file_name)
        thumbnailer = get_thumbnailer(self.avatar_storage, image)
        thumbnail = thumbnailer.get_thumbnail({'size': (50, 50), 'quality': 90})
        return os.path.join(settings.MEDIA_URL, thumbnail.url)


class UserProfile(LocationMixin, models.Model, AvatarImageMixin):
    """This model extends a django user with additional hero information."""
    add_introspection_rules([], ["^herobase\.fields\.LocationField"])

    objects = models.Manager()

    user = models.OneToOneField(User)
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
        return list(User.objects.select_related().order_by( '-userprofile__experience', 'username' )).index(self.user) + 1

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


