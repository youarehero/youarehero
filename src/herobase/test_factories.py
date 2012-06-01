# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from herobase.models import Quest, CLASS_CHOICES, Adventure

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
        'password': 'md5$VB2Ej0s457FF$b1bce604f8dc3e78f9a3058d6bc94b50'
        }
    user_data.update(kwargs)
    if 'password' in kwargs:
        plain_password = kwargs['password']
        user_data['password'] = make_password(plain_password, hasher='md5')
    else:
        plain_password = 'password'
    user =  User.objects.create(**user_data)
    user.plain_password = plain_password
    user.credentials = {'username': user.username, 'password': user.plain_password}
    return user
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

@factory
def create_adventure(quest, **kwargs):
    create_counter = kwargs.pop('create_counter')
    adventure_data = {
        'state': Adventure.STATE_HERO_APPLIED,
        'quest': quest,
    }
    adventure_data.update(kwargs)
    if not 'user' in adventure_data:
        adventure_data['user'] = create_user()
    return Adventure.objects.create(**adventure_data)