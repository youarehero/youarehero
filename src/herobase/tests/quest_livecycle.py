# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import unittest
from django.core.exceptions import ValidationError
from django.test import TestCase
from factories import create_adventure, create_quest, create_user
from herobase.models import Quest


class QuestTest(TestCase):
    """
    Basic Unittests for Quest cycle. (applay, accept, cancel, done, ...)
    """
    def test_owner_cancel(self):
        """If there is a open quest, the owner should be able to cancel that quest."""
        quest = create_quest()
        quest.state.cancel()
        self.assertTrue(quest.canceled)

    def test_hero_apply(self):
        """If there is a open quest, and I'm not the owner,
        I should be able to apply for that quest."""
        quest = create_quest()
        hero = create_user()
        quest.adventure_state(hero).apply()
        self.assertTrue(quest.adventures.filter(user=hero,
                                                accepted=False,
                                                rejected=False,
                                                canceled=False,
                                                done=False).exists())

    def test_hero_apply_started_not_valid(self):
        """If the quest is full, I should not be able to apply for the quest."""
        quest = create_quest(max_heroes=1)
        hero0 = create_user()
        hero1 = create_user()

        quest.adventure_state(hero0).apply()
        quest.adventure_state(hero1).apply()

        #quest_livecycle.owner_hero_accept(quest, hero0)
        quest.adventure_state(hero0).accept()
        quest.state.start()

        with self.assertRaises(ValidationError):
            quest.adventure_state(hero1).accept()

    def test_hero_cancel_not_valid(self):
        """If I'm a hero, not participating in a quest, I should not be able to cancel."""
        quest = create_quest()
        hero = create_user()

        with self.assertRaises(ValidationError):
            quest.adventure_state(hero).cancel()

    def test_hero_cancel(self):
        """If I'm a hero, participating in a quest, I should be able to cancel my participation."""
        quest = create_quest()
        adventure = create_adventure(quest)
        adventure.state.cancel()
        self.assertTrue(quest.adventures.get(user=adventure.user).canceled)

    def test_owner_accept(self):
        """If I'm the owner of a open quest, and a hero is applying,
         I should be able to accept her."""
        quest = create_quest()
        adventure = create_adventure(quest)
        adventure.state.accept()
        self.assertIn(adventure, quest.adventures.accepted())

    def test_owner_done_no_heroes(self):
        """If there was no hero accepted for my quest, I can't mark the quest as "done"."""
        quest = create_quest()
        with self.assertRaises(ValidationError):
            quest.state.done()
        self.assertFalse(quest.done)

    def test_owner_done_valid(self):
        """If there is at least one accepted hero for my quest,
         I should be able to mark the quest as "done"."""
        quest = create_quest()
        adventure = create_adventure(quest, accepted=True)
        quest.state.start()
        quest.state.done()
        self.assertTrue(quest.done)

    def test_owner_done_done_not_valid(self):
        """If my quest is already marked as "done", i should not be able to mark it again."""
        quest = create_quest(done=True)
        adventure = create_adventure(quest, accepted=True)
        with self.assertRaises(ValidationError):
            quest.state.done()
        self.assertTrue(quest.done)

    def test_owner_reject(self):
        """The owner is able to reject a applying hero."""
        quest = create_quest()
        adventure = create_adventure(quest)
        adventure.state.reject()
        self.assertNotIn(adventure, quest.adventures.applying())
        self.assertNotIn(adventure, quest.adventures.accepted())

    def test_find_quests_for_automatic_completion(self):
        quest0 = create_quest(completes_upon_expiration=True, expiration_date=datetime.today())
        quest1 = create_quest(completes_upon_expiration=True,
                              expiration_date=datetime.today() - timedelta(days=1))
        self.assertNotIn(quest0, Quest.objects.expired_but_not_done())
        self.assertIn(quest1, Quest.objects.expired_but_not_done())

    @unittest.expectedFailure
    def test_update_quests_for_automatic_completion_with_min_heroes(self):
        yesterday = datetime.today() - timedelta(days=1)
        quest0 = create_quest(completes_upon_expiration=True,
                              expiration_date=yesterday, min_heroes=0)
        quest1 = create_quest(completes_upon_expiration=True,
                              expiration_date=yesterday, min_heroes=1)
        Quest.objects.update_expired_but_not_done()
        self.assertNotIn(quest0, Quest.objects.expired_but_not_done())
        self.assertNotIn(quest1, Quest.objects.expired_but_not_done())

    def test_auto_accept_hero(self):
        quest = create_quest(auto_accept=True)
        hero = create_user()
        quest.adventure_state(hero).apply()
        self.assertTrue(quest.adventures.filter(user=hero,
                                                accepted=True,
                                                rejected=False,
                                                canceled=False,
                                                done=False).exists())

    def test_accept_all(self):
        quest = create_quest()
        heroes = [create_user() for i in range(3)]
        for hero in heroes:
            quest.adventure_state(hero).apply()

        quest.state.accept_all()
        for hero in heroes:
            self.assertTrue(quest.adventures.filter(user=hero, accepted=True).exists())

    def test_start_needs_min_heroes(self):
        quest = create_quest(auto_accept=True, min_heroes=1)
        hero = create_user()

        with self.assertRaises(ValidationError):
            quest.state.start()

        quest.adventure_state(hero).apply()
        quest.state.start()
        self.assertTrue(quest.started)

