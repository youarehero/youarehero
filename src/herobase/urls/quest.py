# -*- coding: utf-8 -*-
import logging

from django.conf.urls import patterns, include, url
from ..views import QuestCreateView

logger = logging.getLogger(__name__)


urlpatterns = patterns(
    'herobase.views',
    url(regex=r'^(?P<quest_id>\d+)/comment/$',
        view='quest_comment',
        name='quest_comment'),
    url(regex=r'^list/$',
        view='quest_list_view',
        name='quest_list'),
    url(regex=r'^my/$',
        view='quest_my',
        name='quest_my'),
    url(regex=r'^my/created/$',
        view='quest_my_created',
        name='quest_my_created'),
    url(regex=r'^my/joined/$',
        view='quest_my_joined',
        name='quest_my_joined'),
    url(regex=r'^my/done/$',
        view='quest_my_done',
        name='quest_my_done'),
    url(regex=r'^create/$',
        view=QuestCreateView.as_view(),
        name='quest_create'),
    url(regex=r'^(?P<quest_id>\d+)/$',
        view='quest_detail_view',
        name='quest_detail'),

    url(regex=r'^(?P<quest_id>\d+)/owner_update_quest/$',
        view='owner_update_quest',
        name='owner_update_quest'),
    url(regex=r'^(?P<quest_id>\d+)/owner_update_hero/(?P<hero_id>\d+)/$',
        view='owner_update_hero',
        name='owner_update_hero'),
    url(regex=r'^(?P<quest_id>\d+)/hero_update_quest/$',
        view='hero_update_quest',
        name='hero_update_quest'),
)