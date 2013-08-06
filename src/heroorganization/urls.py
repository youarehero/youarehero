# -*- coding: utf-8 -*-
import logging
from django.conf.urls import patterns, include, url
from heroorganization.views import OrganizationDetailView, OrgAdminIndexView, OrgAdminUpdateView


logger = logging.getLogger(__name__)

urlpatterns = patterns(
    '',
    url(regex=r'^public/(?P<name>.+)/$',
        view=OrganizationDetailView.as_view(),
        name='organization_detail'),
    url(regex=r'^admin/$',
        view=OrgAdminIndexView.as_view(),
        name='organization_admin_index'),
    url(regex=r'^admin/(?P<pk>\d+)/$',
        view=OrgAdminUpdateView.as_view(),
        name='organization_admin_update'),
)