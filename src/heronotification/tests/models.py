from django.test import TestCase
from django.core import mail

from heronotification import notify
import herobase.tests.factories as factories


class NotificationTest(TestCase):
    def setUp(self):
        self.quest = factories.create_quest()
        self.adventure = factories.create_adventure(self.quest)
        self.applicant = factories.create_user()

    def test_mail_is_sent(self):
        notify.hero_has_applied(self.applicant, self.adventure)
        self.assertEqual(len(mail.outbox), 1, 'no message sent')

    def test_mail_subject(self):
        notify.hero_has_applied(self.applicant, self.adventure)
        self.assertRegexpMatches(
            mail.outbox[0].subject,
            'beworben',
            'subject invalid')

    def test_mail_body(self):
        notify.hero_has_applied(self.applicant, self.adventure)
        self.assertRegexpMatches(
            mail.outbox[0].body,
            'neue Bewerbung',
            'body invalid')
