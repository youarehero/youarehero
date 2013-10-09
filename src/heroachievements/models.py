from django.contrib.auth.models import User
from django.db import models


class Achievements(object):
    level 1






class UserAchievement(models.Model):
    user = models.ForeignKey(User)

    ACHIEVEMENT_TYPES = {
        "": {"image": "img/achievements/level_up.png", "text": "You have "},
    }
    achievement_type = models.CharField(choices=zip(ACHIEVEMENT_TYPES.keys(),
                                                    ACHIEVEMENT_TYPES.keys()))

    @property
    def image(self):
        return self.ACHIEVEMENT_TYPES[self.achievement_type]['image']



