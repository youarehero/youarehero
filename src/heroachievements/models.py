from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.contrib.comments.models import Comment
from django.contrib.comments.signals import comment_was_posted
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
import achievements
from django.dispatch.dispatcher import receiver
from herobase.models import Quest, Adventure
from herobase.quest_livecycle import notify
from herobase.signals import quest_done


class UserAchievement(models.Model):
    user = models.ForeignKey(User, related_name="achievements")
    achievement_type = models.CharField(choices=achievements.achievement_choices(), max_length=63)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created', )

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

    @property
    def title(self):
        return self.achievement.title

    def __unicode__(self):
        return u"%s %s" % (self.user.username, self.achievement)

    def get_absolute_url(self):
        return reverse("userprofile_private")


def grant(user, achievement):
    if achievement.unique:
        UserAchievement.objects.get_or_create(user=user, achievement_type=achievement.name)
    else:
        UserAchievement.objects.create(user=user, achievement_type=achievement.name)


@receiver(post_save, sender=UserAchievement)
def achievement_notification(instance, raw, created, **kwargs):
    if created:
        notify.achievement(instance.user, instance)


@receiver(post_save, sender=Quest)
def quest_achievements(instance, raw, created, **kwargs):
    if created:
        owner = instance.owner
        num_created = owner.created_quests.count()
        if num_created >= 1:
            grant(owner, achievements.create_quest_1)


@receiver(post_save, sender=Adventure)
def adventure_achievements(instance, raw, created, **kwargs):
    if created:
        hero = instance.user
        num_applied = hero.adventures.count()
        if num_applied >= 1:
            grant(hero, achievements.apply_quest_1)


@receiver(comment_was_posted)
def comment_achievements(comment, request, **kwargs):
    comment_count = Comment.objects.filter(user=comment.user).count()
    if comment_count >= 3:
        grant(comment.user, achievements.commented_3)


@receiver(quest_done)
def quest_done_achievements(quest, **kwargs):
    owner_done_count = quest.owner.created_quests.filter(done=True).count()
    if owner_done_count >= 1:
        grant(quest.owner, achievements.done_quest_owner_1)
    if owner_done_count >= 3:
        grant(quest.owner, achievements.done_quest_owner_3)
    if owner_done_count >= 10:
        grant(quest.owner, achievements.done_quest_owner_10)
    if owner_done_count >= 50:
        grant(quest.owner, achievements.done_quest_owner_50)

    for hero in quest.heroes:
        hero_done_count = hero.adventures.filter(done=True).count()
        if hero_done_count >= 1:
            grant(hero, achievements.done_quest_hero_1)
        if hero_done_count >= 3:
            grant(hero, achievements.done_quest_hero_3)
        if hero_done_count >= 10:
            grant(hero, achievements.done_quest_hero_10)
        if hero_done_count >= 50:
            grant(hero, achievements.done_quest_hero_50)