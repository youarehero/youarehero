# Create your views here.
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic.list import ListView
from herobase.forms import UserProfileEdit
from .models import Message
from .forms import MessageForm
import logging

logger = logging.getLogger('youarehero.heromessage')

@login_required
def message_create(request, user_id=None, message_id=None):
    if message_id:
        original_message = get_object_or_404(Message, pk=message_id, recipient=request.user)
        initial = {'recipient': original_message.sender, 'title': "Re: %s" % original_message.title}
    elif user_id:
        initial = { 'recipient': get_object_or_404(User, pk=user_id)}
    else:
        initial = None

    form = MessageForm(request.POST or None, initial=initial)
    if form.is_valid():
        message = form.save(commit=False)
        message.sender = request.user
        messages.success(request, 'Message successfully sent')
        return HttpResponseRedirect(reverse('message-list'))
    return render(request, 'message/create.html', {'form': form})

@login_required
@require_POST
def message_update(request, message_id):
    message = get_object_or_404(Message, Q(recipient=request.user) | Q(sender=request.user), pk=message_id)
    if 'delete' in request.POST:
        if message.recipient == request.user:
            message.recipient_deleted = datetime.now()
        elif message.sender == request.user:
            message.sender_deleted = datetime.now()
        message.save()
        messages.success(request, "Message successfully deleted")
    return HttpResponseRedirect(reverse("message-list"))

@login_required
def message_list(request):
    return render(request, 'message/list.html',{
             'sent_messages': Message.objects.filter(sender=request.user, sender_deleted=None),
             'received_messages': Message.objects.filter(recipient=request.user, recipient_deleted=None),
            })

@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, pk=message_id)
    if not message.read:
        message.read = datetime.now()
        message.save()
    return render(request, 'message/detail.html', {
        'message': message
    })