# -*- coding: utf-8 -*-
from django.test.testcases import TestCase
from django_dynamic_fixture import G
from herobase.models import Quest
from registration.models import User


class QuestModelTest(TestCase):
    def test_quest_heroes(self):
        quest = G(Quest)
        hero0 = G(User)
        hero1 = G(User)

        quest.adventure_state(hero0).apply()
        quest.adventure_state(hero1).apply()

        quest.adventure_state(hero0).accept()

        self.assertSequenceEqual([hero0], quest.heroes)