# Create your views here.
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views.decorators.http import require_POST


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(request.user.notifications, pk=notification_id)
    if notification.read is None:
        notification.read = now()
        notification.save()
    return {'success': True}