# -*- coding: utf-8 -*-
"""
The factories in this file create the basic You are HERO models with default values.
With keyword arguments you can overwrite the default values.
"""
import datetime
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from herobase.models import Quest, CLASS_CHOICES, Adventure

def factory(f):
    """factory decorator: provides a counter for use as id for example."""
    def decorated(*args, **kwargs):
        if 'create_counter' in kwargs:
            decorated._created = kwargs['create_counter']
        else:
            decorated._created += 1
            kwargs['create_counter'] = decorated._created,
        return f(*args, **kwargs)
    decorated._created = 0
    return decorated


@factory
def create_user(**kwargs):
    """creates a user with username: user_<counter>."""
    create_counter = kwargs.pop('create_counter')
    user_data = {
        'username': 'user_%d'  % create_counter,
        'email': 'user_%d@example.com' % create_counter,
        'is_staff': False,
        'is_superuser': False,
        'password': 'plain$$password'
        }
    user_data.update(kwargs)
    if 'password' in kwargs:
        plain_password = kwargs['password']
        user_data['password'] = "plain$$%s" % plain_password
    else:
        plain_password = 'password'
    user =  User.objects.create(**user_data)
    user.plain_password = plain_password
    user.credentials = {'username': user.username, 'password': user.plain_password}
    return user

@factory
def create_quest(**kwargs):
    """Create a quest. default state is "open". if no owner is given, create one."""
    create_counter = kwargs.pop('create_counter')
    quest_data = {'title': 'quest_%d' % create_counter,
                  'description': 'description',

                  'experience': 1,
                  'hero_class': CLASS_CHOICES[0][0],
                  'due_date': datetime.date.today() + datetime.timedelta(days=1)
    }
    quest_data.update(kwargs)
    if not 'owner' in quest_data:
        quest_data['owner'] = create_user()
    return Quest.objects.create(**quest_data)

@factory
def create_adventure(quest, **kwargs):
    """Creates an adventure. if no user is given, create one."""
    create_counter = kwargs.pop('create_counter')
    adventure_data = {
        'quest': quest,
    }
    adventure_data.update(kwargs)
    if not 'user' in adventure_data:
        adventure_data['user'] = create_user()
    return Adventure.objects.create(**adventure_data)