from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.
from django.db.models.signals import post_save

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

    STATE_DOESNT_EXIST = 2**0
    STATE_HERO_APPLIED = 2**1
    STATE_OWNER_REFUSED = 2**2
    STATE_HERO_CANCELED = 2**3
    STATE_OWNER_ACCEPTED = 2**4
    STATE_HERO_DONE = 2**5

    state = models.IntegerField(default=STATE_HERO_APPLIED, choices=(
        (STATE_DOESNT_EXIST, "doesn't exist")
        (STATE_HERO_APPLIED, 'open'),
        (STATE_OWNER_REFUSED, 'refused'),
        (STATE_HERO_CANCELED, 'canceled'),
        (STATE_OWNER_ACCEPTED, 'assigned'),
        (STATE_HERO_DONE, 'done'),
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


    STATE_OPEN = 2**10
    STATE_FULL = 2**11
    STATE_OWNER_DONE = 2**12
    STATE_OWNER_CANCELED = 2**13

    @property
    def cancelled(self):
        return self.state == Quest.STATE_OWNER_CANCELED

    state = models.IntegerField(default=STATE_OPEN, choices=(
        (STATE_OPEN, 'open'),
        (STATE_FULL, 'full'),
        (STATE_OWNER_DONE, 'done'),
        (STATE_OWNER_CANCELED, 'canceled'),
    ))

    def get_absolute_url(self):
        """Get the url for this quests detail page."""
        return reverse("quest-detail", args=(self.pk,))

    #@property
    def needs_heroes(self):
        """Returns true if there are still open slots in this quest"""
        return self.adventure_set.filter(state=Adventure.STATE_OWNER_ACCEPTED).count() < self.max_heroes

    def state_machine(self, user, action, target_user=None):
        if user == self.owner:
            adventure_user = target_user
        else:
            adventure_user = user
        try:
            adventure = Adventure.objects.get(quest=self, user=adventure_user)
        except Adventure.DoesNotExist:
            adventure = Adventure(user=adventure_user)

        # (quest_state, adventure_state)
        hero_map = {
            'cancel': {(Quest.STATE_OPEN, Adventure.STATE_HERO_APPLIED): Adventure.STATE_HERO_CANCELED,
                        (Quest.STATE_FULL, Adventure.STATE_HERO_APPLIED): Adventure.STATE_HERO_CANCELED },
            'apply' : {(Quest.STATE_OPEN, Adventure.STATE_DOESNT_EXIST): Adventure.STATE_HERO_APPLIED,
                        (Quest.STATE_OPEN, Adventure.STATE_HERO_CANCELED): Adventure.STATE_HERO_APPLIED}
        }
        owner_map = {
            'accept': {(Quest.STATE_OPEN, Adventure.STATE_HERO_APPLIED): Adventure.STATE_OWNER_ACCEPTED},
            'cancel': {(Quest.STATE_OPEN, None): Quest.STATE_OWNER_CANCELED}
        }

        if user == self.owner:
            try:
                state = owner_map[action][(self.state, adventure.state)]
            except KeyError:
                state = owner_map[action][(self.state, None)]
            self.owner_set_state(state, adventure)
        else:
            state = hero_map[action][(self.state, adventure.state)]
            self.hero_set_state(state, adventure)

    def owner_set_state(self, state, adventure):
        if self.state == Adventure.STATE_HERO_APPLIED:
            adventure.state = Adventure.STATE_HERO_APPLIED
            adventure.save()
        elif self.state == Quest.STATE_OWNER_CANCELED:
            self.state = Quest.STATE_OWNER_CANCELED
            self.save()

    def hero_set_state(self, state, adventure):
        if state == Adventure.STATE_HERO_CANCELED:
            adventure.state = Adventure.STATE_HERO_CANCELED
            adventure.save()
        elif state == Adventure.STATE_HERO_APPLIED:
            if self.auto_accept:
                adventure.state = Adventure.STATE_OWNER_ACCEPTED
            else:
                adventure.state = Adventure.STATE_HERO_APPLIED
            adventure.save()



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