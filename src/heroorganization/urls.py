# -*- coding: utf-8 -*-
import logging
from django.conf.urls import patterns, include, url
from heroorganization.views import OrganizationDetailView, OrgAdminIndexView, OrgAdminUpdateView, OrganizationListView


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
        view=OrgAdminUpdateView.as_view(),
        name='organization_admin_update'),
)