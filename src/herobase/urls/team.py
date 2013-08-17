# -*- coding: utf-8 -*-
import logging

from django.conf.urls import patterns, url
from herobase.views import team

logger = logging.getLogger(__name__)

urlpatterns = patterns(
    'herobase.views',
    url(regex=r'(?P<team_name>.+)$', view=team, name="team")
)
