# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
import heromessage.views as views

import logging

logger = logging.getLogger(__name__)

urlpatterns = patterns(
    'heromessage.views',
    url(regex=r'^create/$',
        view=views.message_create,
        name='message_create'),
    url(regex=r'^team/$',
        view=views.message_team,
        name='message_team'),
    url(regex=r'^team/(?P<team>\S+)/$',
        view=views.message_team,
        name='message_team_to'),
    url(regex=r'^to/(?P<user_id>\d+)/$',
        view=views.message_create,
        name='message_to'),  # todo: rename
    url(regex=r'^reply/(?P<message_id>\d+)/$',
        view=views.message_create,
        name='message_reply'),  # todo: rename
    url(regex=r'^$',
        view=views.message_list_in,
        name='message_list_in'),
    url(regex=r'^out/$',
        view=views.message_list_out,
        name='message_list_out'),
    url(regex=r'^(?P<message_id>\d+)/$',
        view=views.message_detail,
        name='message_detail'),
    url(regex=r'^(?P<message_id>\d+)/update/$',
        view=views.message_update,
        name='message_update'),
)
