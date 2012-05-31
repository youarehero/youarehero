# Create your views here.
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic.list import ListView
from herobase.forms import UserProfileEdit
from heromessage.models import Message, MessageForm
import logging

logger = logging.getLogger('youarehero.heromessage')


@login_required
def message_view(request, message_id=None):
    user = request.user
    form = MessageForm()

    if request.method == 'POST':

        form = MessageForm(request.POST)

    if message_id is not None:

        message = Message.objects.get(pk=message_id)

        if 'reply' in request.POST:
            form = MessageForm (initial={'recipient':message.sender, 'title': "Re: %s" % message.title})

        elif 'delete' in request.POST:
            if message.recipient == request.user:
                message.recipient_deleted = datetime.now()
            elif message.sender == request.user:
                message.sender_deleted = datetime.now()
            message.save()

            form = MessageForm()

            messages.success(request, 'Message deleted')

    if form.is_valid():
        new_message = form.save(commit=False)
        new_message.sender = request.user
        new_message.save()
        messages.success(request, 'Message successfully sent')

    form.fields["recipient"].queryset = User.objects.exclude(id=user.id)

    sent_messages = Message.objects.filter(sender=user, sender_deleted__isnull=True).order_by('-sent')
    received_messages = Message.objects.filter(recipient=user, recipient_deleted__isnull=True).order_by('-sent')

    return render(request, 'message/message_view.html',
            {'user': user,
             'form': form,
             'sent_messages': sent_messages,
             'received_messages': received_messages,
            })

@require_POST
@login_required
def message_send(request):

    form = MessageForm(request.POST)

    if form.is_valid():
        new_message = form.save(commit=False)
        new_message.sender = request.user
        new_message.save()
        messages.info(request, "Message successfully sent")

    return HttpResponseRedirect('message-view')


@login_required
def message_detail(request, pk):
    message = get_object_or_404(Message, pk=pk)
    message.read = datetime.now()
    message.save()
    return render(request, 'message/message_detail.html', {
        'message': message
    })