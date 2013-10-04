# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
import unittest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
#from factories import create_adventure, create_quest, create_user
from django_dynamic_fixture import G
from herobase.models import Quest, Adventure


class QuestTest(TestCase):
    """
    Basic Unittests for Quest cycle. (applay, accept, cancel, done, ...)
    """
    def test_owner_cancel(self):
        """If there is a open quest, the owner should be able to cancel that quest."""
        quest = G(Quest)
        quest.state.cancel()
        self.assertTrue(quest.canceled)

    def test_hero_apply(self):
        """If there is a open quest, and I'm not the owner,
        I should be able to apply for that quest."""
        quest = G(Quest)
        hero = G(User)
        quest.adventure_state(hero).apply()
        self.assertTrue(quest.adventures.filter(user=hero,
                                                accepted=False,
                                                rejected=False,
                                                canceled=False,
                                                done=False).exists())

    def test_manual_start_trigger_not_triggered_by_joining_or_time(self):
        quest = G(Quest, min_heroes=1, auto_accept=True,
                  start_trigger=Quest.START_MANUAL,
                  start_date=date.today() - timedelta(days=1))
        hero = G(User)
        Quest.objects.update_start_timer_set_but_not_started()
        quest.adventure_state(hero).apply()

        self.assertFalse(Quest.objects.get(pk=quest.pk).started)

    def test_quest_start_trigger_enough_heroes(self):
        quest = G(Quest, min_heroes=2, auto_accept=True, start_trigger=Quest.START_ENOUGH_HEROES)
        hero0 = G(User)
        hero1 = G(User)

        quest.adventure_state(hero0).apply()
        self.assertFalse(quest.started)
        quest.adventure_state(hero1).apply()
        self.assertTrue(quest.started)

    def test_hero_apply_full_not_valid(self):
        """If the quest is full, I should not be able to apply for the quest."""
        quest = G(Quest, max_heroes=1)
        hero0 = G(User)
        hero1 = G(User)

        quest.adventure_state(hero0).apply()
        quest.adventure_state(hero1).apply()

        #quest_livecycle.owner_hero_accept(quest, hero0)
        quest.adventure_state(hero0).accept()
        quest.state.start()

        with self.assertRaises(ValidationError):
            quest.adventure_state(hero1).accept()

    def test_hero_cancel_not_valid(self):
        """If I'm a hero, not participating in a quest, I should not be able to cancel."""
        quest = G(Quest)
        hero = G(User)

        with self.assertRaises(ValidationError):
            quest.adventure_state(hero).cancel()

    def test_hero_cancel(self):
        """If I'm a hero, participating in a quest, I should be able to cancel my participation."""
        quest = G(Quest)
        adventure = G(Adventure, quest=quest)
        adventure.state.cancel()
        self.assertTrue(quest.adventures.get(user=adventure.user).canceled)

    def test_owner_accept(self):
        """If I'm the owner of a open quest, and a hero is applying,
         I should be able to accept her."""
        quest = G(Quest)
        adventure = G(Adventure, quest=quest)
        adventure.state.accept()
        self.assertIn(adventure, quest.adventures.accepted())

    def test_owner_done_no_heroes(self):
        """If there was no hero accepted for my quest, I can't mark the quest as "done"."""
        quest = G(Quest)
        with self.assertRaises(ValidationError):
            quest.state.done()
        self.assertFalse(quest.done)

    def test_owner_done_valid(self):
        """If there is at least one accepted hero for my quest,
         I should be able to mark the quest as "done"."""
        quest = G(Quest)
        adventure = G(Adventure, quest=quest, accepted=True)
        quest.state.start()
        quest.state.done()
        self.assertTrue(quest.done)

    def test_owner_done_done_not_valid(self):
        """If my quest is already marked as "done", i should not be able to mark it again."""
        quest = G(Quest, done=True)
        adventure = G(Adventure, quest=quest, accepted=True)
        with self.assertRaises(ValidationError):
            quest.state.done()
        self.assertTrue(quest.done)

    def test_owner_reject(self):
        """The owner is able to reject a applying hero."""
        quest = G(Quest)
        adventure = G(Adventure, quest=quest)
        adventure.state.reject()
        self.assertNotIn(adventure, quest.adventures.applying())
        self.assertNotIn(adventure, quest.adventures.accepted())

    def test_find_quests_for_automatic_start(self):
        today = date.today()
        tomorrow = today + timedelta(days=1)

        quest0 = G(Quest, start_trigger=Quest.START_TIMER, start_date=today)
        quest1 = G(Quest, start_trigger=Quest.START_TIMER, start_date=tomorrow)
        quest2 = G(Quest, start_trigger=Quest.START_MANUAL, start_date=today)

        self.assertIn(quest0, Quest.objects.start_timer_set_but_not_started())
        self.assertNotIn(quest1, Quest.objects.start_timer_set_but_not_started())
        self.assertNotIn(quest2, Quest.objects.start_timer_set_but_not_started())

    def test_update_quests_for_automatic_start(self):
        quest0 = G(Quest, start_trigger=Quest.START_TIMER, start_date=date.today(), min_heroes=0)
        quest1 = G(Quest, start_trigger=Quest.START_TIMER, start_date=date.today(), min_heroes=10)

        Quest.objects.update_start_timer_set_but_not_started()

        self.assertTrue(Quest.objects.get(pk=quest0.pk).started)
        self.assertTrue(Quest.objects.get(pk=quest1.pk).started)

    def test_find_quests_for_automatic_completion(self):
        quest0 = G(Quest, end_trigger=Quest.END_TIMER, expiration_date=(date.today() +
                                                                        timedelta(days=1)))
        quest1 = G(Quest, end_trigger=Quest.END_TIMER, expiration_date=(date.today() -
                                                                        timedelta(days=1)))
        self.assertNotIn(quest0, Quest.objects.expired_but_not_done())
        self.assertIn(quest1, Quest.objects.expired_but_not_done())

    def test_update_quests_for_automatic_completion_with_min_heroes(self):
        yesterday = date.today() - timedelta(days=1)
        quest0 = G(Quest, end_trigger=Quest.END_TIMER, expiration_date=yesterday, min_heroes=0)
        quest1 = G(Quest, end_trigger=Quest.END_TIMER, expiration_date=yesterday, min_heroes=1)
        self.assertTrue(quest0.state.can_start())
        self.assertFalse(quest1.state.can_start())
        Quest.objects.update_expired_but_not_done()
        self.assertTrue(Quest.objects.get(pk=quest0.pk).done)
        self.assertTrue(Quest.objects.get(pk=quest1.pk).done)

    def test_auto_accept_hero(self):
        quest = G(Quest, auto_accept=True)
        hero = G(User)
        quest.adventure_state(hero).apply()
        self.assertTrue(quest.adventures.filter(user=hero,
                                                accepted=True,
                                                rejected=False,
                                                canceled=False,
                                                done=False).exists())

    def test_accept_all(self):
        quest = G(Quest)
        heroes = G(User, n=3)
        for hero in heroes:
            quest.adventure_state(hero).apply()

        quest.state.accept_all()
        for hero in heroes:
            self.assertTrue(quest.adventures.filter(user=hero, accepted=True).exists())

    def test_start_needs_min_heroes(self):
        quest = G(Quest, auto_accept=True, min_heroes=1)
        hero = G(User)

        with self.assertRaises(ValidationError):
            quest.state.start()

        quest.adventure_state(hero).apply()
        quest.state.start()
        self.assertTrue(quest.started)

