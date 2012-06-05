"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory, Client
from django.test.testcases import SimpleTestCase, TransactionTestCase
from django.test.utils import override_settings
from herobase.models import Quest, Adventure
from herobase.test_factories import create_adventure
from test_factories import create_quest, create_user


def fake_request(user, path='/'):
    factory = RequestFactory()
    request = factory.get(path)
    request.user = user
    request.session = {}
    return request

class QuestTest(TestCase):
    # canceled quest is canceled

    def test_invalid_action_raises_value_error(self):
        quest = create_quest()
        request = fake_request(quest.owner)
        with self.assertRaises(ValueError):
            quest.process_action(request, 'nosuchaction')

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
        self.assertNotIn(adventure.user, quest.active_heroes())

    def test_owner_accept_valid(self):
        quest = create_quest()
        adventure = create_adventure(quest)
        request = fake_request(quest.owner)
        self.assertIn('accept', adventure.valid_actions_for(request))

    def test_owner_accept(self):
        quest = create_quest()
        adventure = create_adventure(quest)
        request = fake_request(quest.owner)
        adventure.process_action(request, 'accept')
        self.assertIn(adventure.user, quest.accepted_heroes())

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

    def test_owner_refuse_valid(self):
        quest = create_quest()
        adventure = create_adventure(quest)
        request = fake_request(quest.owner)
        self.assertIn('refuse', adventure.valid_actions_for(request))

    def test_owner_refuse(self):
        quest = create_quest()
        adventure = create_adventure(quest)
        request = fake_request(quest.owner)
        adventure.process_action(request, 'refuse')
        self.assertNotIn(adventure.user, quest.accepted_heroes())

    def test_adventure_done_valid(self):
        quest = create_quest()
        adventure = create_adventure(quest, state=Adventure.STATE_OWNER_ACCEPTED)
        request = fake_request(quest.owner)
        self.assertIn('done', adventure.valid_actions_for(request))

    def test_adventure_done(self):
        quest = create_quest()
        adventure = create_adventure(quest, state=Adventure.STATE_OWNER_ACCEPTED)
        request = fake_request(quest.owner)
        adventure.process_action(request, 'done')
        self.assertEqual(adventure.state, Adventure.STATE_OWNER_DONE)

    def test_adventure_done_hero_actions(self):
        quest = create_quest()
        adventure = create_adventure(quest, state=Adventure.STATE_OWNER_DONE)
        request = fake_request(adventure.user)
        self.assertNotIn('hero_apply', quest.valid_actions_for(request))
        self.assertNotIn('hero_cancel', quest.valid_actions_for(request))

    def test_adventure_done_owner_actions(self):
        quest = create_quest()
        adventure = create_adventure(quest, state=Adventure.STATE_OWNER_DONE)
        request = fake_request(quest.owner)
        self.assertNotIn('accept', adventure.valid_actions_for(request))
        self.assertNotIn('refuse', adventure.valid_actions_for(request))
        self.assertNotIn('done', adventure.valid_actions_for(request))

    def test_check_quest_full(self):
        quest = create_quest(max_heroes=1)
        adventure = create_adventure(quest)
        request = fake_request(quest.owner)
        self.assertFalse(quest.is_full())
        adventure.process_action(request, 'accept')
        self.assertTrue(quest.is_full())
        self.assertFalse(quest.is_open())

    def test_check_quest_not_full(self):
        quest = create_quest(max_heroes=2)
        adventure = create_adventure(quest)
        request = fake_request(quest.owner)
        adventure.process_action(request, 'accept')
        self.assertFalse(quest.is_full())
        self.assertTrue(quest.is_open())


class UnauthenticatedIntegrationTest(TestCase):
    def test_homepage(self):
        client = Client()
        response = client.get('/')
        self.assertContains(response, 'Join')

    def test_quest_create(self):
        client = Client()
        response = client.get(reverse('quest-create'))
        self.assertTrue(response, '%s?next=%s' % (reverse('django.contrib.auth.views.login'), reverse('quest-create')))



@override_settings(PASSWORD_HASHERS=('herobase.utils.PlainTextPasswordHasher', ))
class AuthenticatedIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user()
        self.logged_in = self.client.login(**self.user.credentials)

    def test_logged_in(self):
        self.assertTrue(self.logged_in)

    def test_authenticated_homepage(self):
        response = self.client.get('/')
        self.assertContains(response, self.user.username)

    def test_quest_create(self):
        response = self.client.get(reverse('quest-create'))
        self.assertContains(response, 'Level')

        response = self.client.post(reverse('quest-create'), data={
            'title': 'title',
            'description': 'description',
            'hero_class': 1,
            'max_heroes': 1,
            'level': 1,
            'experience': 1,
            'location': 'location',
            'due_date': '11/11/13',
        })
        self.assertTrue(Quest.objects.filter(title='title', owner=self.user).exists())

    def test_quest_list(self):
        quest = create_quest(title='aquestcreated')
        response = self.client.get(reverse('quest-list'))
        self.assertContains(response, 'aquestcreated')

    def test_quest_detail(self):
        quest = create_quest(title='questwithadventure', owner=self.user)
        adventure = create_adventure(quest)
        response = self.client.get(reverse("quest-detail", args=(quest.pk, )))
        self.assertContains(response, quest.title)
        self.assertContains(response, adventure.user.username)

    def test_user_edit(self):
        response = self.client.get(reverse('userprofile-edit'))
        self.assertContains(response, self.user.username)

    def test_user_security_edit(self):
        response = self.client.get(reverse('userprofile-privacy-settings'))
        self.assertContains(response, self.user.username)

    def test_user_profile(self):
        user = create_user()
        response = self.client.get(reverse('userprofile-public', args=(user.username,)))
        self.assertContains(response, user.username)

    def test_quest_details_as_hero(self):
        quest = create_quest()
        response = self.client.get(reverse('quest-detail', args=(quest.pk,)))
        self.assertContains(response, quest.title)

    def test_quest_details_as_owner(self):
        quest = create_quest(owner=self.user)
        response = self.client.get(reverse('quest-detail', args=(quest.pk,)))
        self.assertContains(response, quest.title)