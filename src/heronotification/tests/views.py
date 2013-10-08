# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django_dynamic_fixture import G
from django_webtest import WebTest
from herobase.models import Quest


class NotificationTest(WebTest):
    def test_notifications_shown_on_start_page(self):
        quest = G(Quest, title="A worthy deed")
        owner = quest.owner

        hero = G(User, username="Ein heldenhafter Held")

        quest.adventure_state(hero).apply()

        home_page = self.app.get(reverse("home"), user=owner)
        self.assertContains(home_page, hero.username)
        self.assertContains(home_page.click(hero.username), "A worthy deed")

        quest.adventure_state(hero).accept()

        self.assertNotContains(self.app.get(reverse("home")), hero.username)

        hero_home = self.app.get(reverse("home"), user=hero)

        self.assertContains(hero_home, quest.title)

    def test_notification_list(self):
        quest = G(Quest, title="A worthy deed")
        owner = quest.owner

        applied = G(User, username="Bewerbheld")
        accepted = G(User, username="Akzeptiertheld")

        quest.adventure_state(applied).apply()
        quest.adventure_state(accepted).apply()
        quest.adventure_state(accepted).accept()

        notification_list = self.app.get(reverse("notification_list"), user=owner)
        notification_list.mustcontain(applied.username, accepted.username)
