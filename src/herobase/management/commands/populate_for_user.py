# -*- coding: utf-8 -*-
import logging
from django.contrib.auth.models import User
from django.core.management import BaseCommand
import time
from herobase import quest_livecycle
from herobase.test_factories import create_quest, create_user
import random

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<username>'
    help = 'Create quests and interactions for the specified user'

    def handle(self, *args, **options):
        user = User.objects.get(username=args[0])

        user_quests = [create_quest(owner=user, max_heroes=10) for i in range(3)]
        other_users = [create_user(create_counter=(i+int(time.time()))) for i in range(10)]

        for quest in user_quests:
            for other in random.sample(other_users, random.randint(1,5)):
                quest_livecycle.hero_quest_apply(quest, other)

        other_quests = [create_quest(max_heroes=10) for i in range(5)]
        for quest in other_quests:
            quest_livecycle.hero_quest_apply(quest, user)
            for other in random.sample(other_users, random.randint(1,5)):
                quest_livecycle.hero_quest_apply(quest, other)
