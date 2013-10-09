# Create your views here.
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from heronotification.models import Notification


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(request.user.notifications, pk=notification_id)
    if notification.read is None:
        notification.read = now()
        notification.save()
    return {'success': True}


@login_required
def notification_list(request):
    notifications = Notification.for_user(request.user)
    return render(request, 'heronotification/notification_list.html', {
        'notifications': notifications
    })
