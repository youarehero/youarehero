"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User

from django.test import TestCase
from django.test.client import Client


class BehaviourBase(object):
    def test_evaluate_file(self):
        from morelia import Parser
        Parser().parse_file(self.feature_name).evaluate(self)

    def step_i_access_the_url(self, url):
        r'I access the url "(.*)"'
        self.url = url
        self.client = Client()

    def step_i_am_the_user(self, username):
        'I am the user "(.*)"'
        self.user = User.objects.create(username=username)
        self.user.set_password('pw')
        self.user.save()
        login = self.client.login(username=self.user.username,
            password='pw')
        assert login

    def step_i_see_the_text(self, text):
        r'I see the text "(.+)"'
        response = self.client.get(self.url)
        self.assertContains(response, text)


class HomeFeatureTest(TestCase, BehaviourBase):
    feature_name = 'herobase/features/home.feature'