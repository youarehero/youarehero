from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from herobase.views import QuestListView, QuestDetailView, QuestCreateView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^quest/list$', QuestListView.as_view(), name='quest-list'),
    url(r'^quests/create$', QuestCreateView.as_view(), name='quest-create'),
    url(r'^quests/(?P<pk>\d+)$', QuestDetailView.as_view(), name='quest-detail'),
    url(r'^quests/(?P<quest_id>\d+)/adventure_update', 'herobase.views.adventure_update', name='adventure-update'),
    url(r'^$', 'herobase.views.home_view', name='home'),
    (r'^accounts/', include('registration.urls')),

    # Examples:
    # url(r'^$', 'youarehero.views.home', name='home'),
    # url(r'^youarehero/', include('youarehero.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

from django.conf import settings
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns = patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
            }),
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
            }),
    ) + urlpatterns

