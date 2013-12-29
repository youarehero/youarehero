# -*- coding: utf-8 -*-
from collections import OrderedDict
from django.conf import settings
from django.utils.translation import ugettext as _, pgettext

registry = OrderedDict()


def achievement_choices():
    return zip(registry.keys(), registry.keys())


def get_achievement(name, default=None):
    return registry.get(name, default)


class Achievement(object):
    def __init__(self, name, title, text, image="img/levelstar.png", unique=True):
        self.name = name
        self.title = title
        self.text = text
        self._image = image
        self.unique = unique
        registry[self.name] = self

    def __unicode__(self):
        return self.name

    @property
    def image(self):
        return settings.STATIC_URL + self._image

create_quest_1 = Achievement("create_quest_1", _(u"Quest provider"), _(u"Create your first quest"))

apply_quest_1 = Achievement("apply_quest_1", _(u"Quest applicant"), _(u"Apply for your first quest"))


done_quest_hero_1 = Achievement("done_quest_hero_1",  _(u"Heroic aspirants"), _(u"Carry out a quest"))
done_quest_hero_3 = Achievement("done_quest_hero_3",  _(u"Subhero"), _(u"Carry out three quests"))
done_quest_hero_10 = Achievement("done_quest_hero_10",  _(u"Hero"), _(u"Carry out ten quests"))
done_quest_hero_50 = Achievement("done_quest_hero_50",  _(u"Veteran"), _(u"Carry out fifty quests"))

done_quest_owner_1 = Achievement("done_quest_owner_1",
                                 pgettext("Achievement title", u"Creator"),
                                 _(u"Create a quest that is being carried out"))
done_quest_owner_3 = Achievement("done_quest_owner_3", _(u"Principal"),
                                 _(u"Create three quests that are being carried out"))
done_quest_owner_10 = Achievement("done_quest_owner_10", _(u"Client"),
                                  _(u"Create ten quests that are being carried out"))
done_quest_owner_50 = Achievement("done_quest_owner_50", _(u"Eminence"),
                                  _(u"Create fifty quests that are being carried out"))

commented_3 = Achievement("commented_3", _(u"Commentator"), _(u"Comment on three quests"))

heldsein = Achievement("heldsein", _(u"Gründer-Held"), _(u"Nimm am \"Held sein\"-ARG teil"))

# liked_50 = Achievement("liked_50", "Jedermanns Freund", "Like ")
