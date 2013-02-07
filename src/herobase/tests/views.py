# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.utils import unittest
from herobase.models import Quest
from factories import create_adventure, create_quest, create_user

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
            'remote': True,
            'expiration_date': '11.11.2013',
            'address': 'address',
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

    @unittest.skip("Not implemented right now")
    def test_suggested_quests(self):
        """A user should be presented with quest suggestions."""
        master = create_user()
        quest = create_quest(owner=master, title='suggested_quest_0')
        response = self.client.get(reverse('home'))
        self.assertContains(response, quest.title)

    def test_stats(self):
        """A user should be able to see the statistics."""
        quest = create_quest(title='0')
        response = self.client.get(reverse('stats'))
        self.assertContains(response, 'Stat')
        self.assertContains(response, 'uest')

