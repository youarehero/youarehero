# -*- coding: utf-8 -*-
import logging

from django.conf.urls import patterns, include, url
from herobase.views import QuestUpdateView
from ..views import QuestCreateView

logger = logging.getLogger(__name__)


urlpatterns = patterns(
    'herobase.views',
    url(regex=r'^list/$',
        view='quest_list_view',
        name='quest_list'),
    url(regex=r'^list/archive/$',
        view='quest_list_view',
        kwargs={'archive': True,},
        name='quest_list_archive',),
    url(regex=r'^list/done/$',
        view='quest_list_view',
        kwargs={'done': True,},
        name='quest_list_done',),
    url(regex=r'^my/$',
        view='quest_my',
        name='quest_my'),
    url(regex=r'^create/$',
        view=QuestCreateView.as_view(),
        name='quest_create'),
    url(regex=r'^recreate/(?P<quest_id>\d+)/$',
        view=QuestCreateView.as_view(),
        name='quest_recreate'),
    url(regex=r'^(?P<quest_id>\d+)/$',
        view='quest_detail_view',
        name='quest_detail'),
    url(regex=r'^(?P<pk>\d+)/update/$',
        view=QuestUpdateView.as_view(),
        name='quest_update'),
    url(regex=r'^(?P<pk>\d+)/document/$',
        view='quest_document',
        name='quest_document'),
    url(regex=r'^(?P<quest_id>\d+)/owner_update_quest/$',
        view='owner_update_quest',
        name='owner_update_quest'),
    url(regex=r'^(?P<quest_id>\d+)/owner_update_hero/(?P<hero_id>\d+)/$',
        view='owner_update_hero',
        name='owner_update_hero'),
    url(regex=r'^(?P<quest_id>\d+)/hero_update_quest/$',
        view='hero_update_quest',
        name='hero_update_quest'),
    url(regex=r'^(?P<quest_id>\d+)/like_quest/$',
        view='like_quest',
        name='like_quest'),
)