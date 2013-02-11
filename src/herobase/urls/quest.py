# -*- coding: utf-8 -*-
import logging

from django.conf.urls import patterns, include, url
from ..views import QuestCreateView

logger = logging.getLogger(__name__)


urlpatterns = patterns(
    'herobase.views',
    url(regex=r'^list/$',
        view='quest_list_view',
        name='quest-list'),
    url(regex=r'^my/$',
        view='quest_my',
        name='quest-my'),
    url(regex=r'^create/$',
        view=QuestCreateView.as_view(),
        name='quest-create'),
    url(regex=r'^(?P<quest_id>\d+)/$',
        view='quest_detail_view',
        name='quest-detail'),
    url(regex=r'^(?P<quest_id>\d+)/owner_update_quest/',
        view='owner_update_quest',
        name='owner-update-quest'),
    url(regex=r'^(?P<quest_id>\d+)/owner_update_hero/(?P<hero_id>\d+)/',
        view='owner_update_hero',
        name='owner-update-hero'),
    url(regex=r'^(?P<quest_id>\d+)/hero_update_quest/',
        view='hero_update_quest',
        name='hero-update-quest'),
)