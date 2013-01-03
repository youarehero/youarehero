# -"- coding:utf-8 -"-
"""
This module provides all the basic Quest related models for You are HERO.
The most important are Quest, Userprofile (represents a hero) and Adventure.
This module also contains the ActionMixin, which provides basic logic for model actions.
The model actions connect state logic to the models.
"""
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
from herobase.actions import ActionMixin, action

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
    latitude = models.FloatField(null=True, db_index=True)
    longitude = models.FloatField(null=True, db_index=True)
    address = models.CharField(max_length=255, blank=True)

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
    def active(self):
        """Show only adventures that have not been canceled."""
        return self.exclude(state=Adventure.STATE_HERO_CANCELED)
    def in_progress(self):
        return self.filter(state__in=(Adventure.STATE_HERO_APPLIED,
                                      Adventure.STATE_OWNER_ACCEPTED,
                                      Adventure.STATE_HERO_DONE))
class AdventureManager(models.Manager):
    """Custom Object Manager for Adventures, excluding canceled ones."""
    def get_query_set(self):
        return AdventureQuerySet(model=self.model, using=self._db)
    def active(self):
        """Show only adventures that have not been canceled."""
        return self.get_query_set().active()
    def in_progress(self):
        return self.get_query_set().in_progress()

class Adventure(models.Model, ActionMixin):
    """Model the relationship between a User and a Quest she is engaged in."""

    objects = AdventureManager()

    user = models.ForeignKey(User, related_name='adventures')
    quest = models.ForeignKey('Quest')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # The Adventure States are related to a Quest and a User
    STATE_NOT_SET = 0
    STATE_HERO_APPLIED = 1
    STATE_OWNER_REFUSED = 2
    STATE_HERO_CANCELED = 3
    STATE_OWNER_ACCEPTED = 4
    STATE_HERO_DONE = 5
    STATE_OWNER_DONE = 6

    state = models.IntegerField(default=STATE_NOT_SET, choices=(
        (STATE_NOT_SET, _("state not set")),
        (STATE_HERO_APPLIED, _("applied")),
        (STATE_OWNER_REFUSED,_("rejected")),
        (STATE_HERO_CANCELED, _("canceled")),
        (STATE_OWNER_ACCEPTED, _("accepted")),
        (STATE_HERO_DONE, _("confirmation requested")),
        (STATE_OWNER_DONE, _("participation confirmed")),
        ))

    def __unicode__(self):
        return '%s - %s' % (self.quest.title, self.user.username)

    @action(verbose_name=_("accept"))
    def accept(self, request, validate_only=False):
        """Accept adventure.user as a participant and send a notification."""
        valid = self.quest.is_open() and request.user == self.quest.owner and self.state == Adventure.STATE_HERO_APPLIED
        if validate_only or not valid:
            return valid
        self.state = self.STATE_OWNER_ACCEPTED
        # send a message if acceptance is not instantaneous
        if not self.quest.auto_accept:
            Message.send(get_system_user(), self.user, # TODO FIXME : this shouldn't be a message but a notification
                'Du wurdest als Held Akzeptiert',
                textwrap.dedent('''\
                Du wurdest als Held akzeptiert. Es kann losgehen!
                Verabredet dich jetzt mit dem Questgeber um die Quest zu erledigen.

                Quest: %s''' % request.build_absolute_uri(self.quest.get_absolute_url())))
        self.save()
        # recalculate denormalized quest state (quest might be full now)
        self.quest.check_full()
        self.quest.save()


    @action(verbose_name=_("refuse"))
    def refuse(self, request=None, validate_only=False):
        """Deny adventure.user participation in the quest."""
        # TODO : this should maybe generate a message?
        valid = self.quest.owner == request.user and self.state == self.STATE_HERO_APPLIED
        if validate_only or not valid:
            return valid
        self.state = self.STATE_OWNER_REFUSED
        self.save()

    @action(verbose_name=_("done"))
    def done(self, request=None, validate_only=False):
        """Confirm a users participation in a quest."""
        valid = (self.quest.owner == request.user and
                 self.state == self.STATE_OWNER_ACCEPTED and
                 self.quest.state == Quest.STATE_OWNER_DONE)
        if validate_only or not valid:
            return valid
        profile = self.user.get_profile()
        profile.experience += self.quest.experience
        profile.save()

        self.state = self.STATE_OWNER_DONE
        self.save()

class QuestQuerySet(QuerySet):
    def active(self):
        return self.exclude(state__in=(Quest.STATE_OWNER_DONE, Quest.STATE_OWNER_CANCELED))
    def inactive(self):
        return self.filter(state__in=(Quest.STATE_OWNER_DONE, Quest.STATE_OWNER_CANCELED))
    def open(self):
        return self.filter(state=Quest.STATE_OPEN)


class QuestManager(models.Manager):
    """Custom Quest Object Manager, for active and inactive `Quest` objects"""
    def get_query_set(self):
        return QuestQuerySet(model=self.model, using=self._db)
    def active(self):
        return self.get_query_set().active()
    def inactive(self):
        return self.get_query_set().inactive()
    def open(self):
        return self.get_query_set().open()


class Quest(LocationMixin, ActionMixin, models.Model):
    """A quest, owned by a user."""
    objects = QuestManager()

    owner = models.ForeignKey(User, related_name='created_quests')
    title = models.CharField(max_length=255)
    description = models.TextField()

    location = models.CharField(max_length=255) # TODO : placeholder
    due_date = models.DateTimeField()

    hero_class = models.IntegerField(choices=CLASS_CHOICES, blank=True, null=True)
    heroes = models.ManyToManyField(User, through=Adventure, related_name='quests')

    remote = models.BooleanField(default=False, verbose_name=_(u"Can be done remotely"))

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    max_heroes = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    auto_accept = models.BooleanField(default=False, verbose_name=_("accept automatically"),
        help_text=_("If set heroes will be accepted automatically. "
                    "This means that you won't be able to refuse an offer."))

    QUEST_LEVELS = (
        (1, _('1 (Easy)')),
        (2, _('2 (Okay)')),
        (3, _('3 (Experienced)')),
        (4, _('4 (Challenging)')),
        (5, _('Heroic'))
    )

    level = models.PositiveIntegerField(choices=QUEST_LEVELS)
    experience = models.PositiveIntegerField()

    # States for the Quest. OPEN + FULL = ACTIVE, DONE + CANCELED = INACTIVE
    STATE_NOT_SET = 0
    STATE_OPEN = 1
    STATE_FULL = 2
    STATE_OWNER_DONE = 3
    STATE_OWNER_CANCELED = 4

    QUEST_STATES = (
            (STATE_OPEN , _("open")),
            (STATE_FULL , _("full")),
            (STATE_OWNER_DONE , _("done")),
            (STATE_OWNER_CANCELED , _("cancelled")),
        )

    state = models.IntegerField(default=STATE_OPEN, choices=QUEST_STATES)

    def active_heroes(self):
        """Return all heroes active on a quest. These are accepted heroes
         and heroes who claim to be done."""
        return self.heroes.filter(adventures__quest=self.pk,
            adventures__state__in=(Adventure.STATE_OWNER_ACCEPTED,
                                   Adventure.STATE_HERO_DONE))

    def accepted_heroes(self):
        """Return all accepted heroes and following states (heros who
        are done or claim so)"""
        return self.heroes.filter(adventures__quest=self.pk,
            adventures__state__in=(Adventure.STATE_OWNER_ACCEPTED,
                                   Adventure.STATE_OWNER_DONE,
                                   Adventure.STATE_HERO_DONE))

    def applying_heroes(self):
        """Return all heroes, applying for the quest."""
        return self.heroes.filter(adventures__quest=self.pk,
            adventures__state=Adventure.STATE_HERO_APPLIED)

    def remaining_slots(self):
        """Number of heroes who may participate in the quest until maximum
         number of heroes is achieved"""
        return self.max_heroes - self.accepted_heroes().count()

    def clean(self):
        """Clean function for form validation: Max XPs are associated to quest level"""
        if self.experience and self.level and self.experience > self.level * 100: # TODO experience formula
            raise ValidationError(_('Maximum experience for quest with level {0} is {1}').format(self.level, self.level * 100))


    @action(verbose_name=_("cancel"))
    def hero_cancel(self, request, validate_only=False):
        """Cancels an adventure on this quest."""
        valid = self.is_active() and Adventure.objects.in_progress().filter(quest=self, user=request.user).exists()
        if validate_only or not valid:
            return valid
        adventure = self.adventure_set.get(user=request.user)
        adventure.state = Adventure.STATE_HERO_CANCELED
        adventure.save()
        self.check_full()
        self.save()

    @action(verbose_name=_("apply"))
    def hero_apply(self, request, validate_only=False):
        """Applies a hero to the quest and create an adventure for her."""
        if not self.is_open():
            valid = False
        else:
            try:
                adventure = self.adventure_set.get(user=request.user)
            except Adventure.DoesNotExist:
                valid = True
                    # iff we already have an adventure object the only reason for applying
                # again is a previous cancellation
            else:
                valid = adventure.state in (Adventure.STATE_HERO_CANCELED, )
        if validate_only or not valid:
            return valid

        adventure, created = self.adventure_set.get_or_create(user=request.user)
        # send a message when a hero applies for the first time
        if adventure.state != Adventure.STATE_HERO_CANCELED:
            if self.auto_accept: # TODO FIXME : this should be a notification
                Message.send(get_system_user(), self.owner, 'Ein Held hat sich beworben',
                textwrap.dedent('''\
                Auf eine deiner Quests hat sich ein Held beworben.
                Verabredet euch jetzt um die Quest zu erledigen.

                Quest: %s''' % request.build_absolute_uri(self.get_absolute_url())))
            else:
                Message.send(get_system_user(), self.owner, 'Ein Held hat sich beworben',
                    textwrap.dedent('''\
                    Auf eine deiner Quests hat sich ein Held beworben.
                    Damit er auch mitmachen kann solltest du seine Teilnahme erlauben.
                    Verabredet euch dann um die Quest zu erledigen.

                    Quest: %s''' % request.build_absolute_uri(self.get_absolute_url())))
        if self.auto_accept:
            adventure.state = Adventure.STATE_OWNER_ACCEPTED
        else:
            adventure.state = Adventure.STATE_HERO_APPLIED
        adventure.save()

    @action(verbose_name=_("cancel"))
    def cancel(self, request, validate_only=False):
        """Cancels the whole quest."""
        valid = self.owner == request.user and self.is_active()
        if validate_only or not valid:
            return valid
        self.state = self.STATE_OWNER_CANCELED
        self.save()

    @action(verbose_name=_("mark as done"))
    def done(self, request, validate_only=False):
        """Mark the quest as done. The quest is complete and inactive."""
        valid = self.owner == request.user and self.is_active() and self.accepted_heroes().exists()
        if validate_only or not valid:
            return valid

        self.state = self.STATE_OWNER_DONE
        self.save()

    #### C O N D I T I O N S ####
    def needs_attention(self):
        """Only for playtest. Later there should be Notifications for this."""
        return self.adventure_set.filter(state__in=(Adventure.STATE_HERO_APPLIED,
                                                    Adventure.STATE_HERO_DONE)).exists()

    def is_canceled(self, request=None):
        return self.state == Quest.STATE_OWNER_CANCELED

    def is_open(self, request=None):
        return self.state == Quest.STATE_OPEN

    def is_done(self, request=None):
        return self.state == Quest.STATE_OWNER_DONE

    def is_full(self, request=None):
        return self.state == Quest.STATE_FULL

    def is_active(self, request=None):
        return self.state in (Quest.STATE_OPEN, Quest.STATE_FULL)

    def is_closed(self, request=None):
        return self.state in (Quest.STATE_OWNER_CANCELED, Quest.STATE_OWNER_DONE)

    def check_full(self, request=None):
        """Calculates if quest is full or not. Needs to be called when
        a hero is accepted or cancels his adventure."""
        if self.is_closed():
            return
        if not self.max_heroes:
            return
        if self.accepted_heroes().count() < self.max_heroes:
            self.state = Quest.STATE_OPEN
        else:
            self.state = Quest.STATE_FULL
        self.save()

    #### M I S C ####

    @classmethod
    def get_suggested_quests(cls, user, count):
        """Return a (random) list of suggested quests for the user."""
        quests = Quest.objects.open()
        if user.is_authenticated():
            quests = quests.exclude(owner=user)
        quest_count = quests.count()
        if quest_count > 0:
            return set(quests[randint(0, quest_count - 1)] for i in range(count))
        else:
            return set()

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


