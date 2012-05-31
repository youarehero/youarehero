"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.test.client import RequestFactory
from herobase.models import Quest, Adventure
from herobase.test_factories import create_adventure
from test_factories import create_quest, create_user


from django.conf import settings
from django.utils.importlib import import_module
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY

def fake_request(user, path='/'):
    factory = RequestFactory()
    request = factory.get(path)
    request.user = user
    request.session = {}
    return request

class QuestTest(TestCase):
    # canceled quest is canceled
    def test_owner_cancel(self):
        quest = create_quest()
        request = fake_request(quest.owner)
        self.assertIn('cancel', quest.valid_actions_for(request))
        quest.process_action(request, 'cancel')
        self.assertTrue(quest.is_cancelled())

    def test_other_cancel_not_valid(self):
        quest = create_quest()
        not_owner = create_user()
        request = fake_request(not_owner)
        self.assertNotIn('cancel', quest.valid_actions_for(request))

    def test_other_cancel_denied(self):
        quest = create_quest()
        not_owner = create_user()
        request = fake_request(not_owner)
        with self.assertRaises(PermissionDenied):
            quest.process_action(request, 'cancel')
        self.assertFalse(quest.is_cancelled())

    def test_hero_apply_valid(self):
        quest = create_quest()
        hero = create_user()
        request = fake_request(hero)
        self.assertIn('hero_apply', quest.valid_actions_for(request))

    def test_hero_apply_full_not_valid(self):
        quest = create_quest(state=Quest.STATE_FULL)
        hero = create_user()
        request = fake_request(hero)
        self.assertNotIn('hero_apply', quest.valid_actions_for(request))

    def test_hero_apply(self):
        quest = create_quest()
        hero = create_user()
        request = fake_request(hero)
        quest.process_action(request, 'hero_apply')
        self.assertIn(hero, quest.heroes.all())

    def test_hero_cancel_not_valid(self):
        quest = create_quest()
        hero = create_user()
        request = fake_request(hero)
        self.assertNotIn('hero_cancel', quest.valid_actions_for(request))

    def test_hero_cancel_valid(self):
        quest = create_quest()
        adventure = create_adventure(quest)
        request = fake_request(adventure.user)
        self.assertIn('hero_cancel', quest.valid_actions_for(request))

    def test_hero_cancel(self):
        quest = create_quest()
        adventure = create_adventure(quest)
        request = fake_request(adventure.user)
        quest.process_action(request, 'hero_cancel')
        self.assertNotIn(adventure.user, quest.accepted_heroes())

    def test_owner_accept_valid(self):
        quest = create_quest()
        adventure = create_adventure(quest)
        request = fake_request(quest.owner)
        self.assertIn('accept', adventure.valid_actions_for(request))

    def test_owner_done_no_heroes(self):
        quest = create_quest()
        request = fake_request(quest.owner)
        self.assertNotIn('done', quest.valid_actions_for(request))

    def test_owner_done_valid(self):
        quest = create_quest()
        request = fake_request(quest.owner)
        adventure = create_adventure(quest, state=Adventure.STATE_OWNER_ACCEPTED)
        self.assertIn('done', quest.valid_actions_for(request))

    def test_owner_done_done_not_valid(self):
        quest = create_quest(state=Quest.STATE_OWNER_DONE)
        request = fake_request(quest.owner)
        adventure = create_adventure(quest, state=Adventure.STATE_OWNER_ACCEPTED)
        self.assertNotIn('done', quest.valid_actions_for(request))

