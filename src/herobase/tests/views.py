# -*- coding: utf-8 -*-
import datetime
import pprint
from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.utils import unittest
from django_dynamic_fixture import G
from django_webtest import WebTest
import re
import registration
from registration.models import RegistrationProfile
import mock

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


class RegistrationTest(WebTest):
    def test_minor_can_not_register(self):
        registration_page = self.app.get(reverse("registration_register"))
        registration_form = registration_page.forms[1]
        username = 'jungermensch'
        registration_form['username'] = username
        registration_form['email'] = 'jungermensch@example.com'
        registration_form['password1'] = 'aaa'
        registration_form['password2'] = 'aaa'
        registration_form['date_of_birth'] = '01.01.2000'

        with mock.patch("django.contrib.auth.models.User.email_user") as send_mail:
            response = registration_form.submit()

        self.assertRedirects(response, reverse("registration_below_minimum_age"))
        self.assertFalse(RegistrationProfile.objects.filter(user__username=username).exists())

    def test_adult_can_register(self, ):
        home_page = self.app.get('/')

        registration_page = home_page.click("Registrieren", index=0)

        registration_form = registration_page.forms[1]
        username = 'einuser'
        registration_form['username'] = username
        registration_form['email'] = 'einuser@example.com'
        registration_form['password1'] = 'abc'
        registration_form['password2'] = 'abc'
        registration_form['date_of_birth'] = '01.01.1990'

        with mock.patch("django.contrib.auth.models.User.email_user") as send_mail:
            response = registration_form.submit()
            profile = RegistrationProfile.objects.get(user__username=username)

            subject, text, from_mail = send_mail.call_args_list[0][0]
            self.assertIn(profile.activation_key, text)
            self.assertNotEqual(profile.activation_key, profile.ACTIVATED)


        urls = re.findall('https://example.com(/[^  \n]+)', text)
        confirmation_link = self.app.get(urls[0])

        self.assertRedirects(confirmation_link, reverse("userprofile_edit") + "?first_login=True")

        welcome_page = confirmation_link.follow()

        self.assertContains(welcome_page, username)

        self.assertTrue(User.objects.get(username=username).get_profile().is_legal_adult())

    def test_password_reset(self):
        user = G(User)
        self.assertFalse(User.objects.get(pk=user.pk).check_password('ap'))
        request_reset_page = self.app.get(reverse("auth_password_reset"))
        form = request_reset_page.forms[1]
        form['email'] = user.email

        response = form.submit()
        self.assertRedirects(response, reverse("auth_password_reset_done"))

        self.assertEqual(len(mail.outbox), 1)
        text = mail.outbox[0].body
        urls = re.findall(r'http(?s)://example.com(/[^  \n]+)', text)
        reset_page = self.app.get(urls[0])

        form = reset_page.forms[1]
        form['new_password1'] = 'ap'
        form['new_password2'] = 'ap'
        changed = form.submit()
        self.assertRedirects(changed, reverse("auth_password_reset_complete"))

        self.assertTrue(User.objects.get(pk=user.pk).check_password('ap'))


class LeaderBoardViewTest(WebTest):
    def test_leaderboard_view(self):
        users = []
        for i in range(50):
            user = G(User, username='aHero%s' % i)
            profile = user.profile
            profile.experience = i * 1000
            profile.save()
            users.append(user)
        leaderboard_page = self.app.get(reverse('leader_board'), user=users[0])
        leaderboard_page.mustcontain(*[u.username for u in users])

    def test_profile_leaderboard_view(self):
        users = []
        for i in range(5):
            user = G(User, username='aHero%s' % i)
            profile = user.profile
            profile.experience = i * 1000
            profile.save()
            users.append(user)
        user = users[2]
        profile_page = self.app.get(reverse("userprofile_public", args=(user.username, )),
                                    user=users[0])
        profile_page.mustcontain(*[u.username for u in users])

class ProfileViewTest(WebTest):
    def test_view_profile(self):
        user = G(User, username='ahero')
        profile = user.profile
        profile.about = 'some facts about me'
        profile.save()
        other_user = G(User, username='anotherhero')

        profile_page = self.app.get(reverse("userprofile_public", args=(user.username, )),
                                    user=other_user)

        profile_page.mustcontain("some facts about me", "ahero")

    def test_update_profile(self):
        user = G(User, username='ahero')
        update_page = self.app.get(reverse("userprofile_edit"), user=user)

        form = update_page.forms[0]
        form['about'] = 'these are some facts about me'
        response = form.submit()

        user_profile = UserProfile.objects.get(user=user)
        self.assertEqual('these are some facts about me', user_profile.about)

    def test_update_username(self):
        user = G(User, username='ahero')
        update_page = self.app.get(reverse("userprofile_edit"), user=user)

        form = update_page.forms[0]
        form['username'] = 'aNewHeroName'
        response = form.submit()

        user_profile = UserProfile.objects.get(user=user)
        self.assertEqual('aNewHeroName', user_profile.user.username)

    def test_update_username_exists(self):
        user = G(User, username='ahero')
        user2 = G(User, username='anotherhero')
        update_page = self.app.get(reverse("userprofile_edit"), user=user)

        form = update_page.forms[0]
        form['username'] = 'AnotherHero'
        response = form.submit()
        response.mustcontain(u'Dieser Benutzername ist bereits vergeben.')

        user_profile = UserProfile.objects.get(user=user)
        self.assertEqual('ahero', user_profile.user.username)


class QuestViewTest(WebTest):
    def test_quest_document(self):
        quest = G(Quest, auto_accept=True, min_heroes=1, start_trigger=Quest.START_ENOUGH_HEROES)
        hero = G(User)
        quest.adventure_state(hero).apply()
        quest.state.done()

        detail_page = self.app.get(reverse("quest_detail", args=(quest.pk, )), user=quest.owner)

        form = detail_page.forms['documentation_form']
        form['text'] = 'Ich dokumentiere'

        updated = form.submit()

        self.assertContains(updated.follow(), "Ich dokumentiere")

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

    def test_quest_list_filter_remote(self):
        quest1 = G(Quest, title="ALALAremote", remote=True)
        quest2 = G(Quest, title="ALALAlocal", remote=False)
        list_page = self.app.get(reverse("quest_list"))
        form = list_page.forms['quest_filter_form']
        form['remote'] = 'True'
        response = form.submit()

        self.assertContains(response, "ALALAremote")
        self.assertNotContains(response, "ALALAlocal")

    def test_quest_list_filter_time_effort(self):
        quest1 = G(Quest, title="ALALAtime1", time_effort=1)
        quest2 = G(Quest, title="ALALAtime2", time_effort=2)
        list_page = self.app.get(reverse("quest_list"))
        form = list_page.forms['quest_filter_form']
        form['time_effort'] = '1'
        response = form.submit()

        self.assertContains(response, "ALALAtime1")
        self.assertNotContains(response, "ALALAtime2")

    def test_quest_list_filter_search_title(self):
        quest1 = G(Quest, title="ALALAquest1")
        quest2 = G(Quest, title="ALALAquest2")
        list_page = self.app.get(reverse("quest_list"))
        form = list_page.forms['quest_filter_form']
        form['search'] = 'quest1'
        response = form.submit()

        self.assertContains(response, "ALALAquest1")
        self.assertNotContains(response, "ALALAquest2")

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
        self.assertIn(hero, [a.user for a in quest.adventures.accepted()])


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
            'min_heroes': 1,
            'start_trigger': Quest.START_MANUAL,
            'end_trigger': Quest.END_MANUAL,
            'max_heroes': 1,
            'remote': True,
            'time_effort': 1,
            'start_date': '11.11.2013',
            'expiration_date': '11.11.2014',
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


