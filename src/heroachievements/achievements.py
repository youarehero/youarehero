# -*- coding: utf-8 -*-
from collections import OrderedDict

registry = OrderedDict()


def achievement_choices():
    return zip(registry.keys(), registry.keys())


def get_achievement(name, default=None):
    return registry.get(name, default)


class Achievement(object):
    def __init__(self, name, text, image="img/levelstar.png", unique=True):
        self.name = name
        self.text = text
        self.image = image
        self.unique = unique
        registry[self.name] = self

    def __unicode__(self):
        return self.name


create_quest_1 = Achievement("create_quest_1", "Erstelle deine erste Quest")
create_quest_5 = Achievement("create_quest_5", "Erstelle 5 Quests.")

apply_quest_1 = Achievement("apply_quest_1", "Bewirb dich für deine erste Quest.")
apply_quest_3 = Achievement("apply_quest_3", "Bewirb dich für 3 Quests..")
