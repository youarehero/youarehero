# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.utils import unittest
from django_dynamic_fixture import G
from django_webtest import WebTest
from herobase.models import Quest, UserProfile
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
        response = client.get(reverse('quest_create'))
        self.assertTrue(response, '%s?next=%s' % (reverse('django.contrib.auth.views.login'), reverse('quest_create')))


        #todo be fixxed
        #def test_leaderboard(self):
        #    """An anonymous user can visit the leader board."""
        #    client = Client()
        #   testman = create_user(username='testman')
        #   testman.get_profile().experience = 10*6
        #  testman.get_profile().save()
        # response = client.get(reverse('leader-board'))
        # self.assertEqual(response., testman.username)

class QuestIntegrationTests(WebTest):
    def test_quest_create(self):
        owner = G(User)
        create_page = self.app.get(reverse("quest_create"), user=owner)

        form = create_page.forms[0]
        form['title'] = 'A quest'
        form['description'] = 'do things'
        form['max_heroes'] = '3'
        form['remote'] = 'False'
        form['time_effort'] = '3'
        form['address'] = 'Karlsruhe'

        response = form.submit()
        quest = Quest.objects.get(title='A quest')
        self.assertRedirects(response, reverse("quest_detail", args=(quest.pk, )))

    def test_quest_list(self):
        quest = G(Quest, title="ALALA")
        list_page = self.app.get(reverse("quest_list"))
        self.assertContains(list_page, "ALALA")

    def test_quest_apply(self):
        quest = G(Quest, title="Awesome Task")
        hero = G(User)
        assert quest.adventure_state(hero).can_apply

        quest_url = reverse("quest_detail", args=(quest.pk, ))
        detail_page = self.app.get(quest_url, user=hero)
        detail_page.mustcontain("Awesome Task", "Bewerben")

        response = detail_page.forms['hero-apply'].submit()
        self.assertRedirects(response, quest_url)

        quest = Quest.objects.get(pk=quest.pk)
        assert quest.adventure_state(hero).can_accept

    def test_quest_accept_application(self):
        quest = G(Quest, title="Awesome Task")
        hero = G(User, username='einheld')

        quest.adventure_state(hero).apply()

        quest_url = reverse("quest_detail", args=(quest.pk, ))
        detail_page = self.app.get(quest_url, user=quest.owner)
        detail_page.mustcontain("Awesome Task", hero.username)

        response = detail_page.forms['owner_accept_%s' % hero.pk].submit()
        self.assertRedirects(response, quest_url)
        self.assertIn(hero, [a.user for a in quest.accepted_adventures])


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
        response = self.client.get(reverse('quest_create'))
        self.assertContains(response, 'quest')

        response = self.client.post(reverse('quest_create'), data={
            'title': 'title',
            'description': 'description',
            'hero_class': 1,
            'max_heroes': 1,
            'remote': True,
            'time_effort': 1,
            'expiration_date': '11.11.2013',
            'address': 'address',
            })
        self.assertTrue(Quest.objects.filter(title='title', owner=self.user).exists())

    def test_quest_list(self):
        """A user should be able to visit the quest-list-view."""
        quest = create_quest(title='aquest')
        response = self.client.get(reverse('quest_list'))
        self.assertContains(response, 'aquest')

    def test_quest_detail(self):
        """A owner should be able to see his quest detail-view and a hero applying for that quest."""
        quest = create_quest(title='questwithadventure', owner=self.user)
        adventure = create_adventure(quest)
        response = self.client.get(reverse("quest_detail", args=(quest.pk, )))
        self.assertContains(response, quest.title)
        self.assertContains(response, adventure.user.username)

    def test_user_edit(self):
        """A user should be able to see his userprofile-edit-form."""
        response = self.client.get(reverse('userprofile_edit'))
        self.assertContains(response, self.user.username)

    def test_user_security_edit(self):
        """A user should be able to see his userprofile-privacy-settings-form."""
        response = self.client.get(reverse('userprofile_privacy_settings'))
        self.assertContains(response, self.user.username)

    def test_user_profile(self):
        """A user should be able to see another users public profile."""
        user = create_user()
        response = self.client.get(reverse('userprofile_public', args=(user.username,)))
        self.assertContains(response, user.username)

    def test_quest_details_as_hero(self):
        """A hero can see quest-details."""
        quest = create_quest()
        response = self.client.get(reverse('quest_detail', args=(quest.pk,)))
        self.assertContains(response, quest.title)

    def test_quest_details_as_owner(self):
        """An owner can see quest-details."""
        quest = create_quest(owner=self.user)
        response = self.client.get(reverse('quest_detail', args=(quest.pk,)))
        self.assertContains(response, quest.title)

    @unittest.skip("Not implemented right now")
    def test_suggested_quests(self):
        """A user should be presented with quest suggestions."""
        master = create_user()
        quest = create_quest(owner=master, title='suggested_quest_0')
        response = self.client.get(reverse('home'))
        self.assertContains(response, quest.title)


