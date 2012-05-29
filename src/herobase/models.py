from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.db import models, transaction

# Create your models here.
from django.db.models.signals import post_save
from django.utils.decorators import method_decorator

CLASS_CHOICES =  (
    (0, "Scientist"),
    (1, 'Gadgeteer'),
    (2, 'Diplomat'))


class Adventure(models.Model):
    """Model the relationship between a User and a Quest she is engaged in."""
    user = models.ForeignKey(User, related_name='adventures')
    quest = models.ForeignKey('Quest')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    STATE_NOT_SET = 0
    STATE_HERO_APPLIED = 1
    STATE_OWNER_REFUSED = 2
    STATE_HERO_CANCELED = 3
    STATE_OWNER_ACCEPTED = 4
    STATE_HERO_DONE = 5
    STATE_OWNER_DONE = 6

    state = models.IntegerField(default=STATE_NOT_SET, choices=(
        (STATE_NOT_SET, "doesn't exist"),
        (STATE_HERO_APPLIED, 'applied'),
        (STATE_OWNER_REFUSED, 'refused'),
        (STATE_HERO_CANCELED, 'canceled'),
        (STATE_OWNER_ACCEPTED, 'assigned'),
        (STATE_HERO_DONE, 'hero done'),
        (STATE_OWNER_DONE, 'owner done'),
        ))


class Quest(models.Model):
    """A quest, owned by a user"""
    owner = models.ForeignKey(User, related_name='created_quests')
    title = models.CharField(max_length=255)
    description = models.TextField()

    location = models.CharField(max_length=255) # TODO : placeholder
    due_date = models.DateTimeField()

    hero_class = models.IntegerField(choices=CLASS_CHOICES)
    heroes = models.ManyToManyField(User, through=Adventure, related_name='quests')

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    max_heroes = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    auto_accept = models.BooleanField(default=False)

    level = models.PositiveIntegerField(choices=((1, 'Easy'), (2, 'Okay'), (3, 'Experienced'), (4, 'Challenging'), (5, 'Heroic')))
    experience = models.PositiveIntegerField()

    def active_heroes(self):
        return self.heroes.exclude(adventures__quest=self.pk, adventures__state=Adventure.STATE_HERO_CANCELED)

    def clean(self):
        if self.experience and self.level and self.experience > self.level * 100: # TODO experience formula
            raise ValidationError('Maximum experience for quest with level {0} is {1}'.format(self.level, self.level * 100))

    STATE_NOT_SET = 0
    STATE_OPEN = 1
    STATE_FULL = 2
    STATE_OWNER_DONE = 3
    STATE_OWNER_CANCELED = 4

    def is_cancelled(self):
        return self.state == Quest.STATE_OWNER_CANCELED

    def is_open(self):
        return self.state == Quest.STATE_OPEN

    def is_done(self):
        return self.state == Quest.STATE_OWNER_DONE

    def needs_heroes(self):
        """Returns true if there are still open slots in this quest"""
        if self.is_cancelled() or self.is_done():
            return False
        if not self.max_heroes:
            return True
        else:
            return self.adventure_set.filter(state=Adventure.STATE_OWNER_ACCEPTED).count() < self.max_heroes

    state = models.IntegerField(default=STATE_NOT_SET, choices=(
        (STATE_NOT_SET, 'not set'),
        (STATE_OPEN, 'open'),
        (STATE_FULL, 'full'),
        (STATE_OWNER_DONE, 'done'),
        (STATE_OWNER_CANCELED, 'canceled'),
    ))

    def get_absolute_url(self):
        """Get the url for this quests detail page."""
        return reverse("quest-detail", args=(self.pk,))


class UserProfile(models.Model):
    """Hold extended user information."""
    user = models.OneToOneField(User)
    experience = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=255) # TODO : placeholder
    hero_class = models.IntegerField(choices=CLASS_CHOICES, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @property
    def level(self):
        """Calculate the user's level based on her experience"""
        return self.experience % 1000 + 1 # TODO: correct formula


def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile on user account creation."""
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)


class Location(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    zip_code = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    class Meta:
        abstract = True
        # plz, hausnummer, strasse, stadt, bundesland


# wohin damit?

from registration.signals import user_activated
from django.contrib.auth import login, authenticate

def login_on_activation(sender, user, request, **kwargs):
    """Logs in the user after activation"""
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)

# Registers the function with the django-registration user_activated signal
user_activated.connect(login_on_activation)