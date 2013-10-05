# -*- coding: utf-8 -*-
import logging
import time
import random

from django.contrib.auth.models import User
from django.core.management import BaseCommand

from herobase import quest_livecycle
from herobase.tests.factories import create_quest, create_user


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<username>'
    help = 'Create quests and interactions for the specified user'

    def handle(self, *args, **options):
        create_counter = int(time.time())
        create_quest._created = create_counter
        create_user._created = create_counter

        user = User.objects.get(username=args[0])

        other_users = [create_user() for i in range(10)]
        user_quests = [create_quest(owner=user, max_heroes=10) for i in range(3)]

        for quest in user_quests:
            for other in random.sample(other_users, random.randint(1,5)):
                quest.adventure_state(other).apply()

        other_quests = [create_quest(max_heroes=10) for i in range(5)]
        for quest in other_quests:
            quest.adventure_state(user).apply()
            for other in random.sample(other_users, random.randint(1,5)):
                quest.adventure_state(other).apply()
