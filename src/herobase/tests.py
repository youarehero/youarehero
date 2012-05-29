"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase
from test_factories import create_quest, create_user


class QuestTest(TestCase):
    def test_owner_cancel(self):
        quest = create_quest()
        self.assertIn('cancel', quest.valid_actions_for(quest.owner))
        quest.apply_action('cancel', quest.owner)
        self.assertTrue(quest.is_cancelled())