from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import django.contrib.auth.views as auth_views
from django.views.generic import RedirectView
from django.views.generic.base import TemplateView
from herobase.forms import UserAuthenticationForm
import autocomplete_light
from herobase.views import AgeRequiredRegistrationView, RedirectToProfileActivationView

autocomplete_light.autodiscover()
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(regex=r'^$',
        view='herobase.views.home_view',
        name='home'),
    url(regex=r'^arg/$',
        view=TemplateView.as_view(template_name="herobase/arg.html"),
        name='arg'),
    url(regex=r'^press/$',
        view=TemplateView.as_view(template_name="herobase/press.html"),
        name="press"),
    url(regex=r'^dosanddonts/$',
        view=TemplateView.as_view(template_name="herobase/dosanddonts.html"),
        name="dosanddonts"),
    url(regex=r'^imprint/$',
        view=TemplateView.as_view(template_name="herobase/imprint.html"),
        name="imprint"),
    url(regex=r'^manifesto/$',
        view=TemplateView.as_view(template_name="herobase/manifesto.html"),
        name="manifesto"),
    url(regex=r'^credits/$',
        view=TemplateView.as_view(template_name="herobase/credits.html"),
        name="credits"),
    url(regex=r'^leader/$',
        view='herobase.views.leader_board',
        name="leader_board"),
    url(regex=r'^help/$',
        view=TemplateView.as_view(template_name="herobase/help.html"),
        name='help'),
    url(regex=r'^hotline/$',
        view=TemplateView.as_view(template_name="herobase/hotline.html"),
        name='hotline'),
    url(regex=r'^dismiss_notification/(?P<notification_id>\d+)/$',
        view='heronotification.views.mark_notification_read',
        name='mark_notification_read'),

    url(r'^profile/', include('herobase.urls.profile')),
    url(r'^quest/', include('herobase.urls.quest')),
    url(r'^messages/', include('heromessage.urls')),
    url(r'^recommend/', include('herorecommend.urls')),
    url(r'^team/', include('herobase.urls.team')),

    # auth / registration
    url(regex=r'^accounts/login/$',
        view=auth_views.login,
        kwargs={'template_name': 'registration/login.html', 'authentication_form': UserAuthenticationForm},
        name='auth_login'),
    url(regex=r'^accounts/logout/$',
        view=auth_views.logout,
        kwargs={'template_name': 'registration/logout.html', 'next_page': '/'},
        name='auth_logout'),
    url(regex=r'^accounts/register/$',
        view=AgeRequiredRegistrationView.as_view(),
        name='registration_register'),
    url(regex=r'^accounts/activate/(?P<activation_key>\w+)/$',
        view=RedirectToProfileActivationView.as_view(),
        name='registration_activate'),
    url(regex=r'^below_minimum_age$',
        view=TemplateView.as_view(template_name="herobase/below_minimum_age.html"),
        name='registration_below_minimum_age'),
    (r'^accounts/', include('registration.backends.default.urls')),


    # admin
    url(regex=r'^admin/signups/',
        view='herobase.views.signups'),
    url(r'^admin/', include(admin.site.urls)),

    # misc
    url(regex=r'^favicon\.ico$',
        view=RedirectView.as_view(url='static/img/favicon.ico')),

    # third party apps
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'autocomplete/', include('autocomplete_light.urls')),
    url(r'', include('like_button.urls')),
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
