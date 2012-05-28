"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import datetime
import glob
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django.test import TestCase
from django.test.client import Client
from herobase.models import Quest, CLASS_CHOICES
import os
from models import User


def factory(f):
    def decorated(*args, **kwargs):
        decorated._created += 1
        kwargs['create_counter'] = decorated._created,
        return f(*args, **kwargs)
    decorated._created = 0
    return decorated


@factory
def create_user(**kwargs):
    create_counter = kwargs.pop('create_counter')
    user_data = {
        'username': 'user_%d'  % create_counter,
        'is_staff': False,
        'is_superuser': False,
    }
    user_data.update(kwargs)
    return User.objects.create(**user_data)
create_user.created_count = 0

@factory
def create_quest(**kwargs):
    create_counter = kwargs.pop('create_counter')
    quest_data = {'title': 'quest_%d' % create_counter,
                  'description': 'description',

                  'experience': 1,
                  'hero_class': CLASS_CHOICES[0][0],
                  'level': 1,
                  'due_date': datetime.date.today() + datetime.timedelta(days=1)
    }
    quest_data.update(kwargs)
    if not 'owner' in quest_data:
        quest_data['owner'] = create_user()
    return Quest.objects.create(**quest_data)


class AdventureTest(TestCase):
    def test_quest_create(self):
        quest = create_quest()
        heroes = [ create_user() for i in range(10) ]






# ##################
# BDD Morelia tests
# ##################
#


#html_output_dir = os.environ.get('MORELIA_HTML_OUTPUT_DIR', False)
#
#class BehaviourBase(TestCase):
#    def evaluate_feature(self, feature_name):
#        from morelia import Parser
#        p = Parser()
#        p.parse_file(feature_name)
#        if html_output_dir:
#            file_name = os.path.join(html_output_dir, '%s.html' % feature_name.replace('/','_'))
#            with open(file_name, 'w') as file:
#                report = p.report(self)
#                file.write(report)
#        else:
#            p.evaluate(self)
#
#    @classmethod
#    def print_html(cls):
#        from django.test.utils import setup_test_environment
#        setup_test_environment()
#        test = cls()
#        from morelia import Parser
#        features = glob.glob('*/features/*.feature')
#        for feature in features:
#            p = Parser()
#            print p.parse_file(feature).report(test)
#
#
#    def step_i_access_the_url(self, url):
#        r'I access the url "(.*)"'
#        if not url.startswith('/'):
#            self.url = reverse(url)
#        else:
#            self.url = url
#        self.client = Client()
#
#    def step_i_am_logged_in_as_user(self, username):
#        'I am logged in as user "(.*)"'
#        self.user = User.objects.create(username=username)
#        self.user.set_password('pw')
#        self.user.save()
#        login = self.client.login(username=self.user.username,
#            password='pw')
#        assert login
#
#    def step_i_see_the_text(self, text):
#        r'I see the text "(.+)"'
#        if hasattr(self, 'response'):
#            response = self.response
#        else:
#            response = self.client.get(self.url)
#        self.assertContains(response, text)
#
#    def step_enter_into_form_field(self, value, name):
#        r'I enter "(.*)" into the field "(.*)"'
#        if not hasattr(self, 'form_data'):
#            self.form_data = {}
#        self.form_data[name] = value
#
#    def step_I_submit_the_form(self):
#        self.response = self.client.post(self.url, data=self.form_data, follow=True)
#
#
#    def test_home_feature(self):
#        self.evaluate_feature('herobase/features/home.feature')
#
#    def test_auth_feature(self):
#        self.evaluate_feature('herobase/features/auth.feature')
#
#    def test_quest_feature(self):
#        self.evaluate_feature('herobase/features/quest.feature')
#
#
#    def step_the_user_exists(self, username, password):
#        r'the user "(.*)" with password "(.*)" exists'
#        self.user = User.objects.create(username=username)
#        self.user.set_password(password)
#        self.user.save()
#
#
#    def step_I_am_logged_in_as(self, username):
#        r'I am logged in as "(.*)"'
#        self.assertContains(self.response, 'Logout')
#        self.assertContains(self.response, username)
#
