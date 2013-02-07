# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.test import TestCase
from herobase import quest_livecycle
from factories import create_adventure, create_quest, create_user

class QuestTest(TestCase):
    """
    Basic Unittests for Quest cycle. (applay, accept, cancel, done, ...)
    """
    def test_owner_cancel(self):
        """If there is a open quest, the owner should be able to cancel that quest."""
        quest = create_quest()
        quest_livecycle.owner_quest_cancel(quest)
        self.assertTrue(quest.canceled)

    def test_hero_apply(self):
        """If there is a open quest, and I'm not the owner, I should be able to apply for that quest."""
        quest = create_quest()
        hero = create_user()
        quest_livecycle.hero_quest_apply(quest, hero)

    def test_hero_apply_full_not_valid(self):
        """If the quest is full, I should not be able to apply for the quest."""
        quest = create_quest(max_heroes=1)
        hero0 = create_user()
        hero1 = create_user()

        quest_livecycle.hero_quest_apply(quest, hero0)
        quest_livecycle.hero_quest_apply(quest, hero1)

        quest_livecycle.owner_hero_accept(quest, hero0)

        with self.assertRaises(ValidationError):
            quest_livecycle.owner_hero_accept(quest, hero1)

    def test_hero_cancel_not_valid(self):
        """If I'm a hero, not participating in a quest, I should not be able to cancel."""
        quest = create_quest()
        hero = create_user()

        with self.assertRaises(ValidationError):
            quest_livecycle.hero_quest_cancel(quest, hero)


    def test_hero_cancel(self):
        """If I'm a hero, participating in a quest, I should be able to cancel my participation."""
        quest = create_quest()
        adventure = create_adventure(quest)
        quest_livecycle.hero_quest_cancel(quest, adventure.user)
        self.assertTrue(quest.adventures.get(user=adventure.user).canceled)

    def test_owner_accept(self):
        """If I'm the owner of a open quest, and a hero is applying, I should be able to accept her."""
        quest = create_quest()
        adventure = create_adventure(quest)
        quest_livecycle.owner_hero_accept(quest, adventure.user)
        self.assertIn(adventure.user, quest.accepted_heroes())

    def test_owner_done_no_heroes(self):
        """If there was no hero accepted for my quest, I can't mark the quest as "done"."""
        quest = create_quest()
        with self.assertRaises(ValidationError):
            quest_livecycle.owner_quest_done(quest)
        self.assertFalse(quest.done)

    def test_owner_done_valid(self):
        """If there is at least one accepted hero for my quest, I should be able to mark the quest as "done"."""
        quest = create_quest()
        adventure = create_adventure(quest, accepted=True)
        quest_livecycle.owner_quest_done(quest)
        self.assertTrue(quest.done)

    def test_owner_done_done_not_valid(self):
        """If my quest is already marked as "done", i should not be able to mark it again."""
        quest = create_quest(done=True)
        adventure = create_adventure(quest, accepted=True)
        with self.assertRaises(ValidationError):
            quest_livecycle.owner_quest_done(quest)
        self.assertTrue(quest.done)

    def test_owner_reject(self):
        """The owner is able to reject a applying hero."""
        quest = create_quest()
        adventure = create_adventure(quest)
        quest_livecycle.owner_hero_reject(quest, adventure.user)
        self.assertNotIn(adventure.user, quest.applying_heroes())
        self.assertNotIn(adventure.user, quest.accepted_heroes())


    def test_adventure_done(self):
        """A hero should be able to mark his adventure as "done", if he was accepted."""
        quest = create_quest(done=True)
        adventure = create_adventure(quest, accepted=True)
        quest_livecycle.hero_quest_done(quest, adventure.user)



