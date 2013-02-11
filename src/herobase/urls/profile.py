# -*- coding: utf-8 -*-
import logging

from django.conf.urls import patterns, include, url

logger = logging.getLogger(__name__)

urlpatterns = patterns(
    'herobase.views',
    url(regex=r'^edit/$',
        view='userprofile_edit',
        name='userprofile-edit'),
    url(regex=r'^edit/skills/$',
        view='userprofile_skill_settings',
        name='userprofile-skill-settings'),
    url(regex=r'^private/$',
        view='userprofile',
        name='userprofile-private'),
    url(regex=r'^edit/privacy/$',
        view='userprofile_privacy_settings',
        name='userprofile-privacy-settings'),
    url(regex=r'^public/(?P<username>.+)/$',
        view='userprofile',
        name='userprofile-public')
)