# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

import logging

logger = logging.getLogger(__name__)

urlpatterns = patterns(
    'heromessage.views',
    url(regex=r'^create/$',
        view='message_create',
        name='message_create'),
    url(regex=r'^to/(?P<user_id>\d+)/$',
        view='message_create',
        name='message_to'), # todo: rename
    url(regex=r'^reply/(?P<message_id>\d+)/$',
        view='message_create',
        name='message_reply'), # todo: rename
    url(regex=r'^$',
        view='message_list_in',
        name='message_list_in'),
    url(regex=r'^out/$',
        view='message_list_out',
        name='message_list_out'),
    url(regex=r'^(?P<message_id>\d+)/$',
        view='message_detail',
        name='message_detail'),
    url(regex=r'^(?P<message_id>\d+)/update/$',
        view='message_update',
        name='message_update'),
)