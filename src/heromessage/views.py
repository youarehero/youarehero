# Create your views here.
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from herobase.models import Quest
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext as _
from heronotification import notify

from models import Message
from forms import MessageForm, TeamMessageForm, QuestMessageForm
import logging


logger = logging.getLogger('youarehero.heromessage')


@login_required
def message_create(request, user_id=None, message_id=None):
    original_message = None
    if message_id:
        original_message = get_object_or_404(Message, pk=message_id, recipient=request.user)
        initial = {'recipient': original_message.sender, 'title': "Re: %s" % original_message.title}
    elif user_id:
        initial = {'recipient': get_object_or_404(User, pk=user_id)}
    else:
        initial = None

    form = MessageForm(data=request.POST or None, initial=initial)
    if form.is_valid():
        message = form.save(commit=False)
        message.sender = request.user
        message.in_reply_to = original_message
        message.save()
        messages.success(request, _('Message successfully sent'))
        notify.message_received(message.recipient, message)
        return HttpResponseRedirect(reverse('message_list_out'))

    return render(request, 'message/create.html', {'form': form})


@login_required
def message_team(request, team=None):
    form = TeamMessageForm(data=request.POST or None, initial = {'team': team})

    if form.is_valid():
        users = User.objects.select_related('profile').filter(profile__team = form.cleaned_data['team'])
        for user in users:
            m = Message(
                sender = request.user,
                recipient = user,
                title = form.cleaned_data['title'],
                text = form.cleaned_data['text']
            )
            m.save()
        return HttpResponseRedirect(reverse('message_list_out'))

    return render(request, 'message/create.html', {'form': form})


@login_required
def message_quest_heroes(request, quest_id, group_name):
    quest = get_object_or_404(Quest, pk=quest_id)
    if request.user != quest.owner:
        return HttpResponseForbidden()
    form = QuestMessageForm(data=request.POST or None)

    if form.is_valid():
        if group_name == 'applicants':
            adventures = quest.adventures.applying()
        elif group_name == 'participants':
            adventures = quest.adventures.accepted()
        else:
            return Http404()
        for adventure in adventures.select_related('user'):
            m = Message(
                sender = request.user,
                recipient = adventure.user,
                title = form.cleaned_data['title'],
                text = form.cleaned_data['text']
            )
            m.save()
        return HttpResponseRedirect(reverse('message_list_out'))

    return render(request, 'message/create.html', {'form': form})

@login_required
@require_POST
def message_update(request, message_id):
    message = get_object_or_404(Message, Q(recipient=request.user) | Q(sender=request.user), pk=message_id)
    if 'delete' in request.POST:
        if message.recipient == request.user:
            message.recipient_deleted = now()
        if message.sender == request.user:
            message.sender_deleted = now()
        message.save()
        print message.recipient_deleted, message.sender_deleted
        messages.success(request, _("Message successfully deleted"))
    if 'next' in request.POST:
        return HttpResponseRedirect(request.POST.get('next'))
    return HttpResponseRedirect(reverse("message_list_in"))


@login_required
def message_list_out(request):
    sent_messages = Message.objects.filter(sender=request.user, sender_deleted=None)\
                                   .select_related('recipient', 'sender', 'recipient__profile')
    search = request.GET.get('search', '')
    if search:
        sent_messages = sent_messages.filter(
            Q(recipient__username__icontains=search) |
            Q(title__icontains=search) |
            Q(text__icontains=search)
        )
    return render(request, 'message/list_out.html',{
             'sent_messages': sent_messages,
             'search': search,
             })

@login_required
def message_list_in(request):
    Message.objects.filter(recipient=request.user, read__isnull=True).update(read=now())
    received_messages = Message.objects.filter(recipient=request.user, recipient_deleted=None)\
                                       .select_related('recipient', 'sender', 'sender__profile')
    search = request.GET.get('search', '')
    if search:
        received_messages = received_messages.filter(
            Q(sender__username__icontains=search) |
            Q(title__icontains=search) |
            Q(text__icontains=search)
        )
    return render(request, 'message/list_in.html',{
        'received_messages': received_messages,
        'search': search,
    })

@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, pk=message_id)
    if not message.read:
        message.read = now()
        message.save()
    return render(request, 'message/detail.html', {
        'message': message
    })
