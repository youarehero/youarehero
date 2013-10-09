from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
import achievements
from herobase.models import Quest, Adventure
from herobase.quest_livecycle import notify


class UserAchievement(models.Model):
    user = models.ForeignKey(User, related_name="achievements")
    achievement_type = models.CharField(choices=achievements.achievement_choices(), max_length=63)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def achievement(self):
        return achievements.get_achievement(self.achievement_type)

    @achievement.setter
    def achievement(self, achievement):
        self.achievement_type = achievement.name

    @property
    def image(self):
        return self.achievement.image

    @property
    def text(self):
        return self.achievement.text

    def __unicode__(self):
        return u"%s %s" % (self.user.username, self.achievement)

    class Meta:
        ordering = ('-created', )


def grant(user, achievement):
    if achievement.unique:
        UserAchievement.objects.get_or_create(user=user, achievement_type=achievement.name)
    else:
        UserAchievement.objects.create(user=user, achievement_type=achievement.name)


def quest_achievements(instance, raw, created, **kwargs):
    if created:
        owner = instance.owner
        num_created = owner.created_quests.count()
        if num_created >= 1:
            grant(owner, achievements.create_quest_1)
        if num_created >= 5:
            grant(owner, achievements.create_quest_5)


def adventure_achievements(instance, raw, created, **kwargs):
    if created:
        hero = instance.user
        num_applied = hero.adventures.count()
        if num_applied >= 1:
            grant(hero, achievements.apply_quest_1)
        if num_applied >= 5:
            grant(hero, achievements.apply_quest_3)


post_save.connect(quest_achievements, sender=Quest)
post_save.connect(adventure_achievements, sender=Adventure)


def achievement_notification(instance, raw, created, **kwargs):
    if created:
        notify.achievement(instance.user, instance)


post_save.connect(achievement_notification, sender=UserAchievement)

assert False, "quest completed notification does not register as read"