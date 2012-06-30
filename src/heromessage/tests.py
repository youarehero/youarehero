"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core.urlresolvers import reverse

from django.test import TestCase
from django.test.client import Client
from herobase.test_factories import create_user
from heromessage.models import Message
from django.core import mail


class MessageIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user()
        self.logged_in = self.client.login(**self.user.credentials)
    def test_message_list(self):
        message = Message.objects.create(sender=self.user, recipient=self.user, text='text', title='themailtitle')
        response = self.client.get(reverse('message-list'))
        self.assertContains(response, 'themailtitle')
    def test_message_create_view(self):
        response = self.client.get(reverse('message-create'))
        self.assertContains(response, 'text')
    def test_message_mail_notifiaction_enabled(self):
        profile = self.user.get_profile()
        profile.receive_system_email = True
        profile.receive_private_email = True
        profile.save()
        message = Message.objects.create(sender=self.user, recipient=self.user, text='text', title='themailtitle')
        self.assertIn('themailtitle', mail.outbox[0].subject)
    def test_message_mail_notifiaction_enabled(self):
        profile = self.user.get_profile()
        profile.receive_system_email = False
        profile.receive_private_email = False
        profile.save()
        message = Message.objects.create(sender=self.user, recipient=self.user, text='text', title='themailtitle')
        self.assertFalse(any(mail.outbox))
