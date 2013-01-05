"""
This file demonstrates writing tests using the unittest module.
These will pass when you run "manage.py test".

Some tests...
"""
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory, Client
from django.test.testcases import SimpleTestCase, TransactionTestCase
from django.test.utils import override_settings
from herobase import models
from herobase.models import Quest, Adventure, UserProfile
from herobase.test_factories import create_adventure
from test_factories import create_quest, create_user


def fake_request(user, path='/'):
    """create a fake request for testing purposes."""
    factory = RequestFactory()
    request = factory.get(path)
    request.user = user
    request.session = {}
    return request

class QuestTest(TestCase):
    """
    Basic Unittests for Quest cycle. (applay, accept, cancel, done, ...)
    """

    def test_invalid_action_raises_value_error(self):
        """Not allowed action should raise an exception."""
        quest = create_quest()
        request = fake_request(quest.owner)
        with self.assertRaises(ValueError):
            quest.process_action(request, 'nosuchaction')

    def test_owner_cancel(self):
        """If there is a open quest, the owner should be able to cancel that quest."""
        quest = create_quest()
        request = fake_request(quest.owner)
        self.assertIn('cancel', quest.valid_actions_for(request))
        quest.process_action(request, 'cancel')
        self.assertTrue(quest.is_canceled())

    def test_other_cancel_not_valid(self):
        """If I'm not the owner, I should not be able to cancel the quest."""
        quest = create_quest()
        not_owner = create_user()
        request = fake_request(not_owner)
        self.assertNotIn('cancel', quest.valid_actions_for(request))

    def test_other_cancel_denied(self):
        """If I'm not the owner and I try to process the "cancel" action, I get an exception."""
        quest = create_quest()
        not_owner = create_user()
        request = fake_request(not_owner)
        with self.assertRaises(PermissionDenied):
            quest.process_action(request, 'cancel')
        self.assertFalse(quest.is_canceled())

    def test_hero_apply(self):
        """If there is a open quest, and I'm not the owner, I should be able to apply for that quest."""
        quest = create_quest()
        hero = create_user()
        request = fake_request(hero)
        self.assertIn('hero_apply', quest.valid_actions_for(request))
        quest.process_action(request, 'hero_apply')
        self.assertIn(hero, quest.heroes.all())

    def test_hero_apply_full_not_valid(self):
        """If the quest is full, I should not be able to apply for the quest."""
        quest = create_quest(state=Quest.STATE_FULL)
        hero = create_user()
        request = fake_request(hero)
        self.assertNotIn('hero_apply', quest.valid_actions_for(request))
        with self.assertRaises(PermissionDenied):
            quest.process_action(request, 'hero_apply')
        self.assertNotIn(hero, quest.heroes.all())

    def test_hero_cancel_not_valid(self):
        """If I'm a hero, not participating in a quest, I should not be able to cancel."""
        quest = create_quest()
        hero = create_user()
        request = fake_request(hero)
        self.assertNotIn('hero_cancel', quest.valid_actions_for(request))
        with self.assertRaises(PermissionDenied):
            quest.process_action(request, 'hero_cancel')

    def test_hero_cancel(self):
        """If I'm a hero, participating in a quest, I should be able to cancel my participation."""
        quest = create_quest()
        adventure = create_adventure(quest)
        request = fake_request(adventure.user)
        self.assertIn('hero_cancel', quest.valid_actions_for(request))
        quest.process_action(request, 'hero_cancel')
        self.assertNotIn(adventure.user, quest.active_heroes())

    def test_owner_accept(self):
        """If I'm the owner of a open quest, and a hero is applying, I should be able to accept her."""
        quest = create_quest()
        adventure = create_adventure(quest)
        request = fake_request(quest.owner)
        self.assertIn('accept', adventure.valid_actions_for(request))
        adventure.process_action(request, 'accept')
        self.assertIn(adventure.user, quest.accepted_heroes())

    def test_owner_done_no_heroes(self):
        """If there was no hero accepted for my quest, I can't mark the quest as "done"."""
        quest = create_quest()
        request = fake_request(quest.owner)
        self.assertNotIn('done', quest.valid_actions_for(request))
        with self.assertRaises(PermissionDenied):
            quest.process_action(request, 'done')
        self.assertFalse(quest.is_done())

    def test_owner_done_valid(self):
        """If there is at least one accepted hero for my quest, I should be able to mark the quest as "done"."""
        quest = create_quest()
        request = fake_request(quest.owner)
        adventure = create_adventure(quest, state=Adventure.STATE_OWNER_ACCEPTED)
        self.assertIn('done', quest.valid_actions_for(request))
        quest.process_action(request, 'done')
        self.assertTrue(quest.is_done())

    def test_owner_done_done_not_valid(self):
        """If my quest is already marked as "done", i should not be able to mark it again."""
        quest = create_quest(state=Quest.STATE_OWNER_DONE)
        request = fake_request(quest.owner)
        adventure = create_adventure(quest, state=Adventure.STATE_OWNER_ACCEPTED)
        self.assertNotIn('done', quest.valid_actions_for(request))
        with self.assertRaises(PermissionDenied):
            quest.process_action(request, 'done')
        self.assertTrue(quest.is_done())

    def test_owner_refuse(self):
        """The owner is able to refuse a applying hero."""
        quest = create_quest()
        adventure = create_adventure(quest)
        request = fake_request(quest.owner)
        self.assertIn('refuse', adventure.valid_actions_for(request))
        adventure.process_action(request, 'refuse')
        self.assertNotIn(adventure.user, quest.applying_heroes())
        self.assertNotIn(adventure.user, quest.accepted_heroes())


    def test_adventure_done(self):
        """A hero should be able to mark his adventure as "done", if he was accepted."""
        quest = create_quest(state=Quest.STATE_OWNER_DONE)
        adventure = create_adventure(quest, state=Adventure.STATE_OWNER_ACCEPTED)
        request = fake_request(quest.owner)
        self.assertIn('done', adventure.valid_actions_for(request))
        adventure.process_action(request, 'done')
        self.assertEqual(adventure.state, Adventure.STATE_OWNER_DONE)


    def test_adventure_done_hero_actions(self):
        """If my adventure is done, I'm not able to cancel or apply for the quest again."""
        quest = create_quest()
        adventure = create_adventure(quest, state=Adventure.STATE_OWNER_DONE)
        request = fake_request(adventure.user)
        self.assertNotIn('hero_apply', quest.valid_actions_for(request))
        self.assertNotIn('hero_cancel', quest.valid_actions_for(request))
        with self.assertRaises(PermissionDenied):
            quest.process_action(request, 'hero_apply')
        with self.assertRaises(PermissionDenied):
            quest.process_action(request, 'hero_cancel')

    def test_adventure_done_owner_actions(self):
        """If a hero is done with an adventure, the owner is not able to accept, refuse or mark him done again."""
        quest = create_quest()
        adventure = create_adventure(quest, state=Adventure.STATE_OWNER_DONE)
        request = fake_request(quest.owner)
        self.assertNotIn('accept', adventure.valid_actions_for(request))
        self.assertNotIn('refuse', adventure.valid_actions_for(request))
        self.assertNotIn('done', adventure.valid_actions_for(request))
        with self.assertRaises(PermissionDenied):
            adventure.process_action(request, 'accept')
        with self.assertRaises(PermissionDenied):
            adventure.process_action(request, 'refuse')
        with self.assertRaises(PermissionDenied):
            adventure.process_action(request, 'done')

    def test_check_quest_full(self):
        """A quest with max_heroes=1 should be full, if there is one accepted hero."""
        quest = create_quest(max_heroes=1)
        adventure = create_adventure(quest)
        request = fake_request(quest.owner)
        self.assertFalse(quest.is_full())
        adventure.process_action(request, 'accept')
        self.assertTrue(quest.is_full())
        self.assertFalse(quest.is_open())

    def test_check_quest_not_full(self):
        """A quest with max_heroes=2, shoould be open with one accepted hero."""
        quest = create_quest(max_heroes=2)
        adventure = create_adventure(quest)
        request = fake_request(quest.owner)
        adventure.process_action(request, 'accept')
        self.assertFalse(quest.is_full())
        self.assertTrue(quest.is_open())


class UnauthenticatedIntegrationTest(TestCase):
    """Integration Tests for the public part of the Homepage. Some things should be seen, other not."""
    def test_homepage(self):
        """Check if there is any response, and check for a "join"-button in the home-view."""
        client = Client()
        response = client.get('/')
        self.assertContains(response, 'login')

    def test_quest_create(self):
        """If a anonymous user want to create a quest, he is redirected to the login form."""
        client = Client()
        response = client.get(reverse('quest-create'))
        self.assertTrue(response, '%s?next=%s' % (reverse('django.contrib.auth.views.login'), reverse('quest-create')))


    #todo be fixxed
    #def test_leaderboard(self):
    #    """An anonymous user can visit the leader board."""
    #    client = Client()
     #   testman = create_user(username='testman')
     #   testman.get_profile().experience = 10*6
      #  testman.get_profile().save()
       # response = client.get(reverse('leader-board'))
       # self.assertEqual(response., testman.username)

@override_settings(PASSWORD_HASHERS=('herobase.utils.PlainTextPasswordHasher', ))
class AuthenticatedIntegrationTest(TestCase):
    """Integration tests for protected part of the homepage."""
    def setUp(self):
        """Start with logged in user"""
        self.client = Client()
        self.user = create_user()
        self.logged_in = self.client.login(**self.user.credentials)

    def test_logged_in(self):
        """check login"""
        self.assertTrue(self.logged_in)

    def test_authenticated_homepage(self):
        """check for username on home view."""
        response = self.client.get('/')
        self.assertContains(response, self.user.username)

    def test_quest_create(self):
        """A user should be able to create a quest."""
        response = self.client.get(reverse('quest-create'))
        self.assertContains(response, 'Level')

        response = self.client.post(reverse('quest-create'), data={
            'title': 'title',
            'description': 'description',
            'hero_class': 1,
            'max_heroes': 1,
            'level': 1,
            'experience': 1,

            'due_date': '11.11.2013',
            'address': 'address',
            'location_granularity': 0,
        })
        self.assertTrue(Quest.objects.filter(title='title', owner=self.user).exists())

    def test_quest_list(self):
        """A user should be able to visit the quest-list-view."""
        quest = create_quest(title='aquest')
        response = self.client.get(reverse('quest-list'))
        self.assertContains(response, 'aquest')

    def test_quest_detail(self):
        """A owner should be able to see his quest detail-view and a hero applying for that quest."""
        quest = create_quest(title='questwithadventure', owner=self.user)
        adventure = create_adventure(quest)
        response = self.client.get(reverse("quest-detail", args=(quest.pk, )))
        self.assertContains(response, quest.title)
        self.assertContains(response, adventure.user.username)

    def test_user_edit(self):
        """A user should be able to see his userprofile-edit-form."""
        response = self.client.get(reverse('userprofile-edit'))
        self.assertContains(response, self.user.username)

    def test_user_security_edit(self):
        """A user should be able to see his userprofile-privacy-settings-form."""
        response = self.client.get(reverse('userprofile-privacy-settings'))
        self.assertContains(response, self.user.username)

    def test_user_profile(self):
        """A user should be able to see another users public profile."""
        user = create_user()
        response = self.client.get(reverse('userprofile-public', args=(user.username,)))
        self.assertContains(response, user.username)

    def test_quest_details_as_hero(self):
        """A hero can see quest-details."""
        quest = create_quest()
        response = self.client.get(reverse('quest-detail', args=(quest.pk,)))
        self.assertContains(response, quest.title)

    def test_quest_details_as_owner(self):
        """An owner can see quest-details."""
        quest = create_quest(owner=self.user)
        response = self.client.get(reverse('quest-detail', args=(quest.pk,)))
        self.assertContains(response, quest.title)


    def test_suggested_quests(self):
        """A user should be presented with quest suggestions."""

        master = create_user()
        quest = create_quest(owner=master, title='suggested_quest_0')
        response = self.client.get('/')
        self.assertContains(response, quest.title)

    def test_stats(self):
        """A user should be able to see the statistics."""
        quest = create_quest(title='0', hero_class=3)
        response = self.client.get(reverse('stats'))
        self.assertContains(response, 'Stat')
        self.assertContains(response, 'uest')



#class LeaderBoardTest(TestCase):
#    def test_leaderboard_ok(self):
#        """Check if leaderboard is correctly ordered"""
#        for i in range(7,0,-1):
#            user = create_user()
#            profile = user.get_profile()
#            if (i == 4):
#                theuser = user
#            profile.experience = i * 100
#            profile.save()
#
#        self.assertEqual(list(User.objects.order_by('-userprofile__experience')),
#                                 theuser.get_profile().get_related_leaderboard())
#





