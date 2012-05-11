from django.contrib.auth.models import User
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
    author = models.ForeignKey(User)
    title = models.CharField(max_length=255)
    description = models.TextField()
    hero_class = models.IntegerField(choices=CLASS_CHOICES)
    level = models.PositiveIntegerField(default=1)
    max_heroes = models.PositiveIntegerField()
    location = models.CharField(max_length=255) # TODO : placeholder
    due_date = models.DateTimeField()
    heroes = models.ManyToManyField(User, through=Adventure, related_name='quests')

    STATE_OPEN = 0
    STATE_ASSIGNED = 1
    STATE_DONE = 2
    STATE_CANCELED = 3
    state = models.IntegerField(default=STATE_OPEN, choices=(
        (STATE_OPEN, 'open'),
        (STATE_ASSIGNED, 'assigned'),
        (STATE_DONE, 'done'),
        (STATE_CANCELED, 'canceled'),
    ))

    @property
    def experience(self):
        return 10 * self.level # TODO: correct formula

    @property
    def candidates(self):
        return User.objects.filter(adventures__state='applied')


class UserProfile(models.Model):
    user = models.OneToOneField(User)


    experience = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=255) # TODO : placeholder

    hero_class = models.IntegerField(choices=CLASS_CHOICES)

    @property
    def level(self):
        return self.experience % 1000 + 1 # TODO: correct formula

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)
