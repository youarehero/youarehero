# -*- coding: utf-8 -*-
from collections import OrderedDict
from django.conf import settings
from django.utils.translation import ugettext as _

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

create_quest_1 = Achievement("create_quest_1", _(u"Quest-Ersteller"), _(u"Erstelle deine erste Quest"))

apply_quest_1 = Achievement("apply_quest_1", _(u"Quest-Bewerber"), _(u"Bewirb dich für deine erste Quest."))


done_quest_hero_1 = Achievement("done_quest_hero_1",  _(u"Heldenanwärter"), _(u"Erledige eine Quest."))
done_quest_hero_3 = Achievement("done_quest_hero_3",  _(u"Jungheld"), _(u"Erledige drei Quests."))
done_quest_hero_10 = Achievement("done_quest_hero_10",  _(u"Held"), _(u"Erledige 10 Quests."))
done_quest_hero_50 = Achievement("done_quest_hero_50",  _(u"Veteran"), _(u"Erledige 50 Quests."))

done_quest_owner_1 = Achievement("done_quest_owner_1", _(u"Schaffer"),
                                 _(u"Erstelle eine Quest die erledigt wird."))
done_quest_owner_3 = Achievement("done_quest_owner_3", _(u"Auftraggeber"),
                                 _(u"Erstelle 3 Quests die erledigt werden."))
done_quest_owner_10 = Achievement("done_quest_owner_10", _(u"Klient"),
                                  _(u"Erstelle 10 Quests die erledigt werden."))
done_quest_owner_50 = Achievement("done_quest_owner_50", _(u"Eminenz"),
                                  _(u"Erstelle 50 Quests die erledigt werden."))

commented_3 = Achievement("commented_3", _(u"Kommentator"), _(u"Kommentiere 3 Quests"))

# liked_50 = Achievement("liked_50", "Jedermanns Freund", "Like ")
