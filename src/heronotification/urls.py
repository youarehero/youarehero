from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(regex="mark_read/(?P<notification_id>\d+)/$",
        view='heronotification.views.mark_notification_read',
        name='mark_notification_read'),
    url(regex="^$",
        view='heronotification.views.notification_list',
        name='notification_list'),
)