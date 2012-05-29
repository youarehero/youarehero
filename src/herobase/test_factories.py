# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.models import User
from herobase.models import Quest, CLASS_CHOICES

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
