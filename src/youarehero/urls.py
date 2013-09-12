from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import django.contrib.auth.views as auth_views
from herobase.forms import UserAuthenticationForm
import autocomplete_light
autocomplete_light.autodiscover()
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(regex=r'^$',
        view='herobase.views.home_view',
        name='home'),
    url(regex=r'^abstract/$',
        view='herobase.views.abstract',
        name="abstract"),
    url(regex=r'^imprint/$',
        view='herobase.views.imprint',
        name="imprint"),
    url(regex=r'^leader/$',
        view='herobase.views.leader_board',
        name="leader_board"),

    url(r'^profile/', include('herobase.urls.profile')),
    url(r'^quest/', include('herobase.urls.quest')),
    url(r'^messages/', include('heromessage.urls')),
    url(r'^recommend/', include('herorecommend.urls')),
    url(r'^team/', include('herobase.urls.team')),

    url(regex=r'^dismiss_notification/(?P<notification_id>\d+)/$',
        view='heronotification.views.mark_notification_read',
        name='mark_notification_read'),

    # third party apps
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'autocomplete/', include('autocomplete_light.urls')),

    url(regex=r'^accounts/login/$',
        view=auth_views.login,
        kwargs={
            'template_name': 'registration/login.html',
            'authentication_form': UserAuthenticationForm},
        name='auth_login'),
    url(regex=r'^accounts/register/$',
        view='registration.views.register',
        kwargs={
            'backend': 'herobase.custom_registration.Backend'
        },
        name='registration_register'),
    url(regex=r'^accounts/activate/(?P<activation_key>\w+)/$',
        view='registration.views.activate',
        kwargs={
            'backend': 'herobase.custom_registration.Backend',
            'success_url': '/profile/edit/?first_login=True',
        },
        name='registration_activate'),
    url(r'^accounts/logout/$',
        auth_views.logout,
        {'template_name': 'registration/logout.html',
         'next_page': '/'},
        name='auth_logout'),
    (r'^accounts/', include('registration.backends.default.urls')),
    url(regex=r'^below_minimum_age$',
        view='herobase.views.below_minimum_age',
        name='registration_below_minimum_age'),

    # admin

    url(regex=r'^admin/signups/',
        view='herobase.views.signups'),

    url(r'^admin/', include(admin.site.urls)),

    # misc

    url(regex=r'^favicon\.ico$',
        view='django.views.generic.simple.redirect_to',
        kwargs={'url': 'static/img/favicon.ico'}),

    # like_button

    url(r'', include('like_button.urls'))
)

from django.conf import settings
if settings.DEBUG:
    #noinspection PyAugmentAssignment
    urlpatterns = patterns(
        '',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT}),
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT}),
    ) + urlpatterns

from django.conf import settings

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^rosetta/', include('rosetta.urls')),
    )
