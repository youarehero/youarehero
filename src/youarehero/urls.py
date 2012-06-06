from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from herobase.views import QuestCreateView
import autocomplete_light
autocomplete_light.autodiscover()
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^quest/list/$', 'herobase.views.quest_list_view', name='quest-list'),
    url(r'^quests/create/$', QuestCreateView.as_view(), name='quest-create'),
    url(r'^quests/(?P<quest_id>\d+)/$', 'herobase.views.quest_detail_view', name='quest-detail'),
    url(r'^quests/(?P<quest_id>\d+)/quest_update/',
        'herobase.views.quest_update', name='quest-update'),
    url(r'^quests/(?P<quest_id>\d+)/adventure_update/',
        'herobase.views.adventure_update', name='adventure-update'),
    url(r'^$', 'herobase.views.home_view', name='home'),

    url(r'^profile/$', 'herobase.views.userprofile_edit', name='userprofile-edit'),
    url(r'^profile/privacy/$', 'herobase.views.userprofile_privacy_settings', name='userprofile-privacy-settings'),
    url(r'^profile/(?P<username>[\w.@+-]+)/$', 'herobase.views.userprofile_public', name='userprofile-public'),

    url(r'^messages/reply/(?P<message_id>\d+)/$', 'heromessage.views.message_list', name='message-list'), # todo: rename
    url(r'^messages/', 'heromessage.views.message_list', name='message-list'),
    url(r'^message/(?P<pk>\d+)/$', 'heromessage.views.message_detail', name='message-detail'),
   # url(r'^message/send', 'heromessage.views.message_send', name='message-send'),

    url(r'^stats/$', 'herobase.views.random_stats', name="stats"),
    url(r'^leader/$', 'herobase.views.leader_board', name="leader-board"),
    # Examples:
    # url(r'^$', 'youarehero.views.home', name='home'),
    # url(r'^youarehero/', include('youarehero.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:

    url(r'^admin/', include(admin.site.urls)),
    url(r'autocomplete/', include('autocomplete_light.urls')),
    (r'^accounts/', include('registration.backends.default.urls')),
)

from django.conf import settings
if settings.DEBUG:
    #noinspection PyAugmentAssignment
    urlpatterns = patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
            }),
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
            }),
    ) + urlpatterns

