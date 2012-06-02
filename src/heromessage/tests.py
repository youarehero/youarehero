"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core.urlresolvers import reverse

from django.test import TestCase
from django.test.client import Client
from herobase.test_factories import create_user


class MessageIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user()
        self.logged_in = self.client.login(**self.user.credentials)
    def test_message_list(self):
        response = self.client.get(reverse('message-list'))
        self.assertContains(response, 'In')