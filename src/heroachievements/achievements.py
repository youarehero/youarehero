# -*- coding: utf-8 -*-
from collections import OrderedDict
from django.conf import settings

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

create_quest_1 = Achievement("create_quest_1", u"Quest-Ersteller", u"Erstelle deine erste Quest")

apply_quest_1 = Achievement("apply_quest_1", u"Quest-Bewerber", u"Bewirb dich für deine erste Quest.")


done_quest_hero_1 = Achievement("done_quest_hero_1",  u"Heldenanwärter", u"Erledige eine Quest.")
done_quest_hero_3 = Achievement("done_quest_hero_3",  u"Jungheld", u"Erledige drei Quests.")
done_quest_hero_10 = Achievement("done_quest_hero_10",  u"Held", u"Erledige 10 Quests.")
done_quest_hero_50 = Achievement("done_quest_hero_50",  u"Veteran", u"Erledige 50 Quests.")

done_quest_owner_1 = Achievement("done_quest_owner_1", u"Schaffer",
                                 u"Erstelle eine Quest die erledigt wird.")
done_quest_owner_3 = Achievement("done_quest_owner_3", u"Auftraggeber",
                                 u"Erstelle 3 Quests die erledigt werden.")
done_quest_owner_10 = Achievement("done_quest_owner_10", u"Klient",
                                  u"Erstelle 10 Quests die erledigt werden.")
done_quest_owner_50 = Achievement("done_quest_owner_50", u"Eminenz",
                                  u"Erstelle 50 Quests die erledigt werden.")

commented_3 = Achievement("commented_3", u"Kommentator", u"Kommentiere 3 Quests")

# liked_50 = Achievement("liked_50", "Jedermanns Freund", "Like ")