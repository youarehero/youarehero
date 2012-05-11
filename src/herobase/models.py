from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models

# Create your models here.
from django.db.models.signals import post_save

CLASS_CHOICES =  (
    (0, "Scientist"),
    (1, 'Gadgeteer'),
    (2, 'Diplomat'))


class Adventure(models.Model):
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


class Quest(models.Model):
    author = models.ForeignKey(User, related_name='authored_quests')
    title = models.CharField(max_length=255)
    description = models.TextField()
    hero_class = models.IntegerField(choices=CLASS_CHOICES)
    level = models.PositiveIntegerField(default=1)
    max_heroes = models.PositiveIntegerField()
    location = models.CharField(max_length=255) # TODO : placeholder
    due_date = models.DateTimeField()
    heroes = models.ManyToManyField(User, through=Adventure, related_name='quests')
    created = models.DateTimeField(auto_now_add=True)
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

    @property
    def experience(self):
        return 10 * self.level # TODO: correct formula

    @property
    def candidates(self):
        return User.objects.filter(adventures__state='applied')

    def get_absolute_url(self):
        return reverse("quest-detail", args=(self.pk,))

    #@property
    def needs_heroes(self):
        if self.heroes.filter(adventures__state=Adventure.STATE_ASSIGNED).count() < self.max_heroes:
            return True
        return False

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    experience = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=255) # TODO : placeholder
    hero_class = models.IntegerField(choices=CLASS_CHOICES, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @property
    def level(self):
        return self.experience % 1000 + 1 # TODO: correct formula


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)
