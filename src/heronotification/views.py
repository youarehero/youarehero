# Create your views here.
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from herobase.utils import login_required


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(request.user.notifications, pk=notification_id)
    if notification.read is None:
        notification.read = datetime.now()
        notification.save()
    return {'success': True}