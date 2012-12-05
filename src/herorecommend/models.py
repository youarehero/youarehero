from math import sqrt
from django.contrib.auth.models import User
from django.contrib.localflavor.hr.forms import postal_code_re
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from herobase.models import Quest



SELECTION_PROFILE_WEIGHT = 1.0

SKILLS = ["example%d" % i for i in range(50)]

# Rating stuff:
# on event [apply/participate/cancel/...] -> rate quest for user
#
#

# Profile updates:
# on event [user: create] -> create all profiles for user
# on event [quest: create] -> create questprofile

# on questrating update -> update userratingprofile -> update usercombinedprofile
# on userselectionprofile update -> update usercombinedprofile


class SkillBase(models.Model):
    def get_skills(self):
        return [skill for skill in SKILLS if getattr(self, skill)]

    class Meta:
        abstract = True

for skill in SKILLS:
    SkillBase.add_to_class(skill, models.FloatField(default=0))


class QuestProfile(SkillBase):
    quest = models.OneToOneField(Quest, related_name='profile')
    average = models.FloatField(default=0)
    root_sum_of_squares = models.FloatField(default=0)

    def save(self, force_insert=False, force_update=False, using=None):
        self.average = sum(getattr(self, skill) for skill in SKILLS) / float(len(SKILLS))
        self.root_sum_of_squares =  sum(getattr(self, skill)**2 for skill in SKILLS)**.5

        for skill in SKILLS:
            delta_skill = getattr(self, skill) - self.average
            setattr(self, "delta_%s" % skill, delta_skill)
        return super(QuestProfile, self).save(force_insert, force_update, using)

for skill in SKILLS:
    QuestProfile.add_to_class('delta_%s' % skill, models.FloatField(default=0))


class UserSelectionProfile(SkillBase):
    user = models.OneToOneField(User, related_name='selected_skills')


class UserRatingProfile(SkillBase):
    user = models.OneToOneField(User, related_name='rating_profile')

    @property
    def average(self):
        return sum([getattr(self, skill) for skill in SKILLS]) / float(len(SKILLS))

    @property
    def norm(self):
        return sqrt(sum([getattr(self, skill)**2 for skill in SKILLS]))

    @classmethod
    def rate(cls, user, quest, old_rating, new_rating):
        delta_rating = (new_rating - old_rating)
        user_profile, created = UserRatingProfile.objects.get_or_create(user=user)
        quest_profile = quest.profile

        for skill in SKILLS:
            current = getattr(user_profile, skill)
            updated = current + delta_rating * getattr(quest_profile, skill)
            setattr(user_profile, skill, updated)

        user_profile.save()
        combined, created = UserCombinedProfile.objects.get_or_create(user=user)
        combined.update()

    def reset(self):
        for skill in SKILLS:
            setattr(self, skill, 0.0)
        for rating in self.user.ratings.all().select_related('quest__profile'):
            for skill in SKILLS:
                current = getattr(self, skill)
                delta = rating.rating * getattr(rating.quest.profile, skill)
                setattr(self, skill, current + delta)
        self.save()
    reset.alters_data = True

class UserCombinedProfile(SkillBase):
    user = models.OneToOneField(User, related_name='combined_profile')

    @property
    def average(self):
        return sum([getattr(self, skill) for skill in SKILLS]) / float(len(SKILLS))

    @property
    def norm(self):
        return sqrt(sum([getattr(self, skill)**2 for skill in SKILLS]))

    def reset(self):
        self.user.rating_profile.reset()
        self.update()
    reset.alters_data = True

    def update(self):
        selection_profile, created = UserSelectionProfile.objects.get_or_create(user=self.user)
        rating_profile, created = UserRatingProfile.objects.get_or_create(user=self.user)

        rating_norm = rating_profile.norm
        for skill in SKILLS:
            if rating_norm:
                weight = (getattr(selection_profile, skill) * SELECTION_PROFILE_WEIGHT +
                          getattr(rating_profile, skill) / rating_norm)
            else:
                weight = getattr(selection_profile, skill) * SELECTION_PROFILE_WEIGHT
            setattr(self, skill, weight)
        self.save()
    update.alters_data = True


RATING_WEIGHTS = {
    'like': 0.3,
    'apply': 0.7,
    'participate': 0.8,
    'participate_plus': 1.0,
}

RATING_PRECEDENCE_ORDER = [ 'participate_plus', 'participate', 'apply', 'like']
RATED_ACTIONS =  ['participate_plus', 'participate', 'apply', 'like']

class QuestRating(models.Model):
    user = models.ForeignKey(User, related_name='ratings')
    quest = models.ForeignKey(Quest)

    like = models.NullBooleanField(null=True)
    apply = models.NullBooleanField(null=True)
    participate = models.NullBooleanField(null=True)
    participate_plus = models.NullBooleanField(null=True)

    @property
    def rating(self):
        for field in RATING_PRECEDENCE_ORDER:
            if getattr(self, field):
                return RATING_WEIGHTS[field]
        return 0

    @classmethod
    def rate(cls, user, quest, action):
        if not action in RATED_ACTIONS:
            raise ValueError("Not a valid action: %s" % action)

        quest_rating, created = cls.objects.get_or_create(user=user, quest=quest)

        old_rating = quest_rating.rating
        setattr(quest_rating, action, True)
        quest_rating.save()
        new_rating = quest_rating.rating

        if old_rating != new_rating:
            UserRatingProfile.rate(user, quest, old_rating, quest_rating.rating)

        return quest_rating



@receiver(post_save, sender=UserSelectionProfile)
def update_combined_profile(sender, instance=None, **kwargs):
    if instance:
        instance.user.combined_profile.update()

@receiver(post_save, sender=User)
def create_user_rating_profiles(sender, instance=None, created=False, **kwargs):
    if created:
        UserSelectionProfile.objects.get_or_create(user=instance)
        UserRatingProfile.objects.get_or_create(user=instance)
        UserCombinedProfile.objects.get_or_create(user=instance)

