# -*- coding: utf-8 -*-
import logging

from django.conf.urls import patterns, include, url

logger = logging.getLogger(__name__)

urlpatterns = patterns(
    'herorecommend.views',
    url(regex=r'^$',
        view='recommend',
        name='recommend'),
    url(regex=r'^rate/(?P<quest_id>\d+),(?P<rating>\d)/$',
        view='rate',
        name='rate'),
)

