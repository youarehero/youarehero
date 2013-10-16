"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.core import mail
from django.test.utils import override_settings
from django_dynamic_fixture import G
from django_webtest import WebTest

from herobase.tests.factories import create_user
from heromessage.models import Message


@override_settings(PASSWORD_HASHERS=('herobase.utils.PlainTextPasswordHasher', ))
class MessageIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user()
        self.logged_in = self.client.login(**self.user.credentials)

    def test_message_list_in(self):
        message = Message.objects.create(sender=self.user, recipient=self.user, text='text', title='themailtitle')
        response = self.client.get(reverse('message_list_in'))
        self.assertContains(response, 'themailtitle')

    def test_message_list_out(self):
        message = Message.objects.create(sender=self.user, recipient=self.user, text='text', title='themailtitle')
        response = self.client.get(reverse('message_list_out'))
        self.assertContains(response, 'themailtitle')

    def test_message_create_view(self):
        response = self.client.get(reverse('message_create'))
        self.assertContains(response, 'text')

    #TODO: FIX test_message_mail_notification_enabled
    #def test_message_mail_notification_enabled(self):
    #    profile = self.user.get_profile()
    #    profile.receive_system_email = True
    #    profile.receive_private_email = True
    #    profile.save()
    #    message = Message.objects.create(sender=self.user, recipient=self.user, text='text', title='themailtitle')
    #    print mail, mail.outbox
    #    self.assertIn('themailtitle', mail.outbox[0].subject)

    def test_message_mail_notification_disabled(self):
        profile = self.user.get_profile()
        profile.receive_system_email = False
        profile.receive_private_email = False
        profile.save()
        message = Message.objects.create(sender=self.user, recipient=self.user, text='text', title='themailtitle')
        self.assertFalse(any(mail.outbox))

class MessageWebTest(WebTest):
    def test_message_list_in_search(self):
        user = G(User, username='ahero')
        message1 = G(Message, sender=user, recipient=user, text='text1', title='themailtitle1',
                     sender_deleted=None, recipient_deleted=None)
        message2 = G(Message, sender=user, recipient=user, text='text2', title='themailtitle2',
                     sender_deleted=None, recipient_deleted=None)
        list_page = self.app.get(reverse('message_list_in'), user=user)
        form = list_page.forms['message_filter_form']
        form['search'] = 'text1'
        response = form.submit()
        self.assertContains(list_page, 'themailtitle1')
        self.assertNotContains(response, 'themailtitle2')

    def test_message_list_out_search(self):
        user = G(User, username='ahero')
        message1 = G(Message, sender=user, recipient=user, text='text1', title='themailtitle1',
                     sender_deleted=None, recipient_deleted=None)
        message2 = G(Message, sender=user, recipient=user, text='text2', title='themailtitle2',
                     sender_deleted=None, recipient_deleted=None)
        list_page = self.app.get(reverse('message_list_out'), user=user)
        form = list_page.forms['message_filter_form']
        form['search'] = 'text1'
        response = form.submit()
        self.assertContains(response, 'themailtitle1')
        self.assertNotContains(response, 'themailtitle2')

    def test_message_list_in_delete(self):
        user = G(User, username='ahero')
        message1 = G(Message, sender=user, recipient=user, text='text1', title='themailtitle1',
                     sender_deleted=None, recipient_deleted=None)
        message2 = G(Message, sender=user, recipient=user, text='text2', title='themailtitle2',
                     sender_deleted=None, recipient_deleted=None)
        list_page = self.app.get(reverse('message_list_in'), user=user)
        form = list_page.forms['delete_message_%s' % message2.pk]
        response = form.submit('delete')
        self.assertRedirects(response, reverse('message_list_in'))
        self.assertContains(response.follow(), 'themailtitle1')
        self.assertNotContains(response.follow(), 'themailtitle2')

    def test_message_list_out_delete(self):
        user = G(User, username='ahero')
        message1 = G(Message, sender=user, recipient=user, text='text1', title='themailtitle1',
                     sender_deleted=None, recipient_deleted=None)
        message2 = G(Message, sender=user, recipient=user, text='text2', title='themailtitle2',
                     sender_deleted=None, recipient_deleted=None)
        list_page = self.app.get(reverse('message_list_out'), user=user)
        form = list_page.forms['delete_message_%s' % message2.pk]
        response = form.submit('delete')
        self.assertRedirects(response, reverse('message_list_out'))
        self.assertContains(response.follow(), 'themailtitle1')
        self.assertNotContains(response.follow(), 'themailtitle2')