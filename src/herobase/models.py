# -"- coding:utf-8 -"-
"""
This module provides all the basic Quest related models for You are HERO.
The most important are Quest, Userprofile (represents a hero) and Adventure.
This module also contains the ActionMixin, which provides basic logic for model actions.
The model actions connect state logic to the models.
"""
from datetime import datetime, timedelta, date
import glob
from random import randint
from django.contrib.comments.signals import comment_was_posted
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

from .quest_livecycle import QuestState, AdventureState
from heromessage.models import Message
from herobase.utils import is_legal_adult

QUEST_EXPERIENCE = 1000
CREATE_EXPERIENCE = 50
APPLY_EXPERIENCE = 10
COMMENT_EXPERIENCE = 10

# The classes a User can choose from. (Hero classes)
CLASS_CHOICES =  (
    (5, "Scientist"),
    (1, 'Gadgeteer'),
    (2, 'Diplomat'),
    (3, 'Action'),
    (4, 'Protective'))
SEX_CHOICES =  (
    (1, 'Männlich'),
    (2, 'Weiblich'))

AVATAR_IMAGES_TRUSTED = sorted(map(
    lambda x: os.path.join('avatar', os.path.basename(x)),
    glob.glob(os.path.join(settings.ASSET_ROOT, 'avatar', '*'))
))
AVATAR_IMAGES = filter(
    lambda fname: fname.endswith(".png"),
    AVATAR_IMAGES_TRUSTED
)


class Like(models.Model):
    user = models.ForeignKey(User, related_name='likes')
    quest = models.ForeignKey('Quest', related_name='likes')


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

    location_granularity = models.IntegerField(
        default=LOCATION_GRANULARITY_NONE,
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

    def save(self, *args, **kwargs):
        if (self.latitude and self.longitude
                and self.location_granularity == self.LOCATION_GRANULARITY_NONE):
            self.location_granularity = self.LOCATION_GRANULARITY_UNKNOWN
        return super(LocationMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class AdventureQuerySet(QuerySet):
    def applying(self):
        """Show only adventures that have not been canceled."""
        return self.filter(canceled=False, accepted=False, rejected=False)

    def accepted(self):
        return self.filter(canceled=False, accepted=True, rejected=False)

    def rejected(self):
        return self.filter(canceled=False, accepted=False, rejected=True)

    def pending(self):
        return self.filter(canceled=False, accepted=False, rejected=False)


class AdventureManager(models.Manager):
    """Custom Object Manager for Adventures, excluding canceled ones."""
    def get_query_set(self):
        return AdventureQuerySet(model=self.model, using=self._db)

    def applying(self):
        """Show only adventures that have not been canceled."""
        return self.get_query_set().applying()

    def accepted(self):
        return self.get_query_set().accepted()

    def rejected(self):
        return self.get_query_set().rejected()

    def pending(self):
        return self.get_query_set().pending()


class Adventure(models.Model):
    @property
    def state(self):
        return AdventureState(self.quest if self.quest_id else None,
                              self.user if self.user_id else None,
                              self)

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

    def save(self, *args, **kwargs):
        if not self.user.profile.is_legal_adult()\
                and not self.quest.owner.profile.trusted:
            raise ValidationError("Minors are not allowed to participate in "
                                  "quests by untrusted users")

        if self.accepted and not self.accepted_time:
            self.accepted_time = now()
        if self.rejected and not self.rejected_time:
            self.rejected_time = now()
        if self.done and not self.done_time:
            self.done_time = now()
        if self.canceled and not self.canceled_time:
            self.canceled_time = now()
        return super(Adventure, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s - %s' % (self.quest.title, self.user.username)

    def get_absolute_url(self):
        return self.quest.get_absolute_url()

    def get_state_display(self):
        if self.canceled:
            return _(u"cancelled")
        elif self.accepted:
            return _(u"participating")
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

    def start_timer_set_but_not_started(self):
        return self.get_query_set().filter(
            start_trigger=Quest.START_TIMER,
            start_date__lte=datetime.now(),
            canceled=False,
            done=False,
            started=False,
        )

    def update_start_timer_set_but_not_started(self):
        for quest in self.start_timer_set_but_not_started():
            quest.state.force_start()

    def expired_but_not_done(self):
        return self.get_query_set().filter(
            end_trigger=Quest.END_TIMER,
            expiration_date__lt=datetime.now(),
            canceled=False,
            done=False,
        )

    def update_expired_but_not_done(self):
        for quest in self.expired_but_not_done():
            quest.state.force_done()


class Quest(LocationMixin, models.Model):
    """A quest, owned by a user."""
    objects = QuestManager()

    owner = models.ForeignKey(User, related_name='created_quests')
    title = models.CharField(max_length=255, verbose_name=_(u"Title"))
    description = models.TextField(verbose_name=_(u"Description"),
                                   help_text=_(u"A short description of what "
                                               u"this quest is about."))

    START_MANUAL = 0
    START_TIMER = 1
    START_ENOUGH_HEROES = 2
    START_CHOICES = (
        (START_MANUAL, "Manuell"),
        (START_TIMER, "Zum Startzeitpunkt"),
        (START_ENOUGH_HEROES, "Genug Helden"),
    )

    END_MANUAL = 0
    END_TIMER = 1
    END_CHOICES = (
        (END_MANUAL, "Manuell"),
        (END_TIMER, "Zum End-Datum"),
    )

    start_trigger = models.IntegerField(choices=START_CHOICES, default=START_MANUAL,
                                        verbose_name=_(u"Quest-Beginn"))
    end_trigger = models.IntegerField(choices=END_CHOICES, default=END_MANUAL,
                                      verbose_name=_(u"Quest-Ende"))

    start_date = models.DateTimeField(blank=True, null=True, verbose_name=_(u"Startzeitpunkt"))
    expiration_date = models.DateTimeField(default=lambda: now() + timedelta(days=30),
                                           verbose_name=_(u"Expiration date"),
                                           help_text=_(u"Until which date will "
                                                       u"this quest be visible?"))

    heroes = models.ManyToManyField(User, through=Adventure, related_name='quests')

    remote = models.BooleanField(default=True, verbose_name=_(u"Can be done remotely"),
                                 help_text=_(u"Can this quest be done remotely or only locally?"))

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    min_heroes = models.PositiveIntegerField(default=0, verbose_name="Minimale Helden-Anzahl")
    max_heroes = models.PositiveIntegerField(default=1,
                                             validators=[MinValueValidator(1)],
                                             verbose_name=_(u"Number of heroes"),
                                             help_text=_(u"How many heroes "
                                                         u"can participate in "
                                                         u"this Quest?"))
    auto_accept = models.BooleanField(
        default=False,
        verbose_name="Automatisch annehmen",
        help_text="Helden die sich bewerben werden automatisch angenommen."
    )

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

    TIME_EFFORT_LOW = 1
    TIME_EFFORT_MEDIUM = 2
    TIME_EFFORT_HIGH = 3
    time_effort = models.IntegerField(null=True, verbose_name=_(u"time effort"), choices=(
        (TIME_EFFORT_LOW, _(u"Low")),
        (TIME_EFFORT_MEDIUM, _(u"Medium")),
        (TIME_EFFORT_HIGH, _(u"High")),
    ))

    @property
    def has_expired(self):
        return self.expiration_date < now()

    @property
    def state(self):
        return QuestState(self)

    def adventure_state(self, hero):
        return AdventureState(self, hero)

    @property
    def likes_count(self):
        return self.likes.all().count()

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.owner.profile.is_legal_adult():
            raise ValidationError("Minors are not allowed to create quests")

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

    EDIT_WINDOW_MINUTES = 10

    @property
    def edit_window_expired(self):
        return (now() - self.modified) > timedelta(minutes=self.EDIT_WINDOW_MINUTES)

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


class AvatarImageMixin(models.Model):
    avatar_storage = FileSystemStorage(location=settings.ASSET_ROOT)
    image = models.FilePathField(blank=True, null=True)

    def clean(self):
        images = AVATAR_IMAGES_TRUSTED if self.trusted else AVATAR_IMAGES
        if self.image not in images:
            raise ValidationError(_("Invalid avatar image given"))

    @classmethod
    def avatar_choices(cls):
        def t(avatar):
            thumbnailer = get_thumbnailer(cls.avatar_storage, avatar)
            thumbnail = thumbnailer.get_thumbnail({'size': (50, 83), 'quality': 90})
            return os.path.join(settings.MEDIA_URL, thumbnail.url)
        return [(name, t(name)) for name in AVATAR_IMAGES]

    def avatar(self):
        """Return a String, containing a path to a thumbnail-image 270x270."""
        return self._avatar_thumbnail((150, 250))

    @property
    def avatar_thumbnail(self):
        """Return a String, containing a path to a thumbnail-image 50x50."""
        return self._avatar_thumbnail((50, 50))

    @property
    def avatar_quest_list(self):
        """Return a String, containing a path to a thumbnail-image 40x40."""
        return self._avatar_thumbnail((50, 50))

    @property
    def avatar_thumbnail_40(self):
        """Return a String, containing a path to a thumbnail-image 40x40."""
        return self._avatar_thumbnail((40, 40))

    @property
    def avatar_thumbnail_70(self):
        """Return a String, containing a path to a thumbnail-image 80x80."""
        return self._avatar_thumbnail((70, 70))

    @property
    def avatar_thumbnail_80(self):
        """Return a String, containing a path to a thumbnail-image 80x80."""
        return self._avatar_thumbnail((80, 80))
    @property
    def avatar_thumbnail_110(self):
        """Return a String, containing a path to a thumbnail-image 110x110."""
        return self._avatar_thumbnail((110, 110))

    @property
    def avatar_thumbnail_30(self):
        """Return a String, containing a path to a thumbnail-image 30x30."""
        return self._avatar_thumbnail((30, 30))

    def _avatar_thumbnail(self, size, crop='0,0'):
        """Return a String, containing a path to a thumbnail-image."""
        file_name = self.image or 'avatar/default.png'
        thumbnailer = get_thumbnailer(self.avatar_storage, file_name)
        thumbnail = thumbnailer.get_thumbnail({'size': size, 'quality': 90, 'crop':crop})
        return os.path.join(settings.MEDIA_URL, thumbnail.url)

    class Meta:
        abstract = True


class UserProfile(LocationMixin, AvatarImageMixin, models.Model):
    """This model extends a django user with additional hero information."""
    add_introspection_rules([], ["^herobase\.fields\.LocationField"])

    objects = models.Manager()

    user = models.OneToOneField(User, related_name='profile')
    experience = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=255) # TODO : placeholder
    hero_class = models.IntegerField(choices=CLASS_CHOICES, blank=True,
        null=True)
    sex = models.IntegerField(choices=SEX_CHOICES, blank=True, null=True, verbose_name=_(u"sex"))

    date_of_birth = models.DateField(default=date.fromtimestamp(0))

    team = models.CharField(max_length=255, default="", blank=True)

    keep_email_after_gpn = models.DateTimeField(blank=True, null=True,
        editable=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    trusted = models.BooleanField(default=False)

    public_location = models.BooleanField(default=False,
        verbose_name=_("Location is public"),
        help_text=_("Enable this if you want to share "
                    "your location with other Heroes."))

    about = models.TextField(blank=True, default='', verbose_name=_(u"about me"),
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


    levels = [0, 1000, 2000, 4000, 7000, 10000000]
    @property
    def level(self):
        """Calculate the user's level based on her experience"""
        for index, experience in enumerate(self.levels):
            if experience > self.experience:
                return index

    @property
    def next_level_experience(self):
        return self.levels[self.level]

    @property
    def relative_level_experience(self):
        """Calculates percentage of XP for current level."""
        current_level = self.levels[self.level - 1]
        next_level = self.levels[self.level]
        return int(100.0 * (self.experience - current_level)/(next_level-current_level))

    @property
    def unread_messages_count(self):
        """Return number of unread messages."""
        return Message.objects.filter(recipient=self.user,read__isnull=True,
            recipient_deleted__isnull=True).count()

    @property
    def unread_messages_and_notifications_count(self):
        """Returns the number of unread messages and notifications. """
        from heronotification.models import Notification
        return (self.unread_messages_count +
                Notification.objects.filter(user=self.user, read=None).count())

    @property
    def rank(self):
        return UserProfile.objects.filter(experience__gt=self.experience).count() + 1

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

    def is_legal_adult(self):
        return is_legal_adult(self.date_of_birth)


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


def experience_for_comment(sender, comment, request, **kwargs):
    if comment.user_id:
        profile = comment.user.profile
        profile.experience += COMMENT_EXPERIENCE
        profile.save()

comment_was_posted.connect(experience_for_comment)


def create_user_profile(instance, raw, created, using, **kwargs):
    if created:
        profile, created = UserProfile.objects.using(using).get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)
