from django.contrib.auth.models import User
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

    STATE_APPLIED = 0
    STATE_REFUSED = 1
    STATE_CANCELED = 2
    STATE_ASSIGNED = 3
    STATE_DONE = 4

    state = models.IntegerField(choices=(
        (STATE_APPLIED, 'open'),
        (STATE_REFUSED, 'refused'),
        (STATE_CANCELED, 'canceled'),
        (STATE_ASSIGNED, 'assigned'),
        (STATE_DONE, 'done'),
        ))

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

class Quest(models.Model):
    """A quest, owned by a user"""
    owner = models.ForeignKey(User, related_name='created_quests')
    title = models.CharField(max_length=255)
    description = models.TextField()
    hero_class = models.IntegerField(choices=CLASS_CHOICES)
    location = models.CharField(max_length=255) # TODO : placeholder
    due_date = models.DateTimeField()
    heroes = models.ManyToManyField(User, through=Adventure, related_name='quests')
    created = models.DateTimeField(auto_now_add=True)
    max_heroes = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    modified = models.DateTimeField(auto_now=True)

    STATE_OPEN = 0
    STATE_FULL = 1
    STATE_DONE = 2
    STATE_CANCELED = 3
    state = models.IntegerField(default=STATE_OPEN, choices=(
        (STATE_OPEN, 'open'),
        (STATE_FULL, 'full'),
        (STATE_DONE, 'done'),
        (STATE_CANCELED, 'canceled'),
    ))

    def get_absolute_url(self):
        """Get the url for this quests detail page."""
        return reverse("quest-detail", args=(self.pk,))

    #@property
    def needs_heroes(self):
        """Returns true if there are still open slots in this quest"""
        return self.adventure_set.filter(state=Adventure.STATE_ASSIGNED).count() < self.max_heroes

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
