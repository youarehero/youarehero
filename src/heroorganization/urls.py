# -*- coding: utf-8 -*-
import logging
from django.conf.urls import patterns, include, url
from heroorganization.views import OrganizationDetailView, OrganizationListView, organization_update_view


logger = logging.getLogger(__name__)

urlpatterns = patterns(
    '',
    url(regex=r'^$',
        view=OrganizationListView.as_view(),
        name='organization_list'),
    url(regex=r'^profile/(?P<name>.+)/$',
        view=OrganizationDetailView.as_view(),
        name='organization_detail'),
    url(regex=r'^admin/$',
        view=organization_update_view,
        name='organization_update'),
)