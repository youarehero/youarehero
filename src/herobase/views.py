# -*- coding: utf-8 -*-
"""
The Views module provide view functions, which were called by the
`url dispatcher <https://docs.djangoproject.com/en/1.4/topics/http/urls/>`_,
and aggregate some data for use in templates.
"""
from datetime import timedelta
import logging

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Max, Q
from django.utils import simplejson as json
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView

from herobase import quest_livecycle
from heronotification.models import Notification
from herorecommend import recommend
from herorecommend.forms import UserSkillEditForm
from filters import QuestFilter
from herobase.forms import QuestCreateForm, UserProfileEdit, UserProfilePrivacyEdit, CommentForm, UserAuthenticationForm
from herobase.models import Quest, Adventure, CLASS_CHOICES, UserProfile, Like, Comment, CREATE_EXPERIENCE
import herorecommend.signals as recommender_signals
from herorecommend.models import MIN_SELECTED_SKILLS

logger = logging.getLogger('youarehero.herobase')



@login_required
@require_POST
def quest_comment(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    last_creation_time = Comment.objects.filter(author=request.user).aggregate(last_comment_time=Max('created'))['last_comment_time']
    if last_creation_time and now() - last_creation_time < timedelta(seconds=30):
        messages.warning(request, "Du must ein wenig warten bevor du wieder posten kannst.")
        return HttpResponseRedirect(reverse('quest_detail', args=(quest.pk, )))

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.quest = quest
        comment.save()
    return HttpResponseRedirect(reverse('quest_detail', args=(quest.pk, )))


def quest_list_view(request, template='herobase/quest/list.html'):
    """Basic quest list, with django-filter app"""
    if request.user.is_authenticated():
        f = QuestFilter(request.GET, queryset=recommend(request.user, order_by=['-created']))
    else:
        f = QuestFilter(request.GET, queryset=Quest.objects.open().order_by('-created'))
    return render(request, template, {
        'filter': f,
        'quests': f.qs,
    })

class QuestCreateView(CreateView):
    """Basic Quest create view. This generic view-class should be refactored to a normal view function"""
    context_object_name = "quest"
    form_class = QuestCreateForm
    template_name = "herobase/quest/create.html"
    success_url = '../%(id)s/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(QuestCreateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(QuestCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        self.object.owner.get_profile().experience += CREATE_EXPERIENCE
        self.object.owner.get_profile().save()
        return HttpResponseRedirect(self.get_success_url())


def quest_detail_view(request, quest_id):
    """Render detail template for quest, and adventure if it exists."""
    quest = get_object_or_404(Quest, pk=quest_id)

    is_owner = request.user == quest.owner
    if request.user.is_authenticated():
        try:
            adventure = quest.adventures.get(user_id=request.user.pk, canceled=False)
        except Adventure.DoesNotExist:
            adventure = None
    else:
        adventure = None

    if is_owner:
        butler_text = u'Dies ist ihre Quest.'
    elif not adventure:
        butler_text = u"This quest needs heroes. Apply now by clicking the ✓ Button on the right."
    elif adventure.accepted:
        butler_text = u"Your application has been accepted. Press X to withdraw your participation."
    elif adventure.rejected:
        butler_text = u"You have applied for this quest but the owner didn't want you to participate in it."
    elif not adventure.accepted and not adventure.rejected:
        butler_text = (u"You are currently applying for this quest. Press X to cancel."
                      u" You will be notified once the creator has decided about our participation" )
    else:
        butler_text = u"Hello"

    context = {
        'quest': quest,
        'butler_text': butler_text,
        'is_owner': is_owner,
        'comment_form': CommentForm(),
        'request_user_adventure': adventure,

    }

    # {% if not request_user_adventure %}
    # {% trans "" %}
    # {% elif request_user_adventure.accepted %}
    # {% trans " %}
    # {% elif request_user_adventure.rejected %}
    # {% trans "Your application has been rejected." %}
    # {% elif not request_user_adventure.accepted and not request.user.rejected %}
    # {% trans "You are currently applying for this quest. Press X to cancel." %}
    # {% endif %}



    return render(request, "herobase/quest/detail.html", context)

def home_view(request):
    """Proxy view for switching between the hero and the public home view"""
    if request.user.is_authenticated():
        return hero_home_view(request)
    return render(request, "herobase/public_home.html", {
        'open_quests': Quest.objects.open(),
        'form': UserAuthenticationForm()})


def m_home_view(request):
    """Proxy view for switching between the hero and the public home view"""
    return hero_home_view(request, template='herobase/m/home.html')
#    return render(request, "herobase/m/public_home.html", {'open_quests':
#        Quest.objects.filter(state=Quest.STATE_OPEN)})

def abstract(request):
    """static you are hero abstract view."""
    return render(request, "herobase/abstract.html")


def imprint(request):
    """static you are hero imprint view."""
    return render(request, "herobase/imprint.html")

def hero_classes(request):
    """static view for explaining hero classes."""
    return render(request, "herobase/hero_classes.html")

@login_required
def hero_home_view(request, template='herobase/hero_home.html'):
    """the hero home is only visible for authenticated heros."""
    user = request.user
    return render(request, template,
            {
             #'profile': user.get_profile(),
             'notifications': Notification.for_user(user),
#             'quests_active': user.created_quests.filter(canceled=False, done=False).order_by('-created')[:10],
#             'quests_old': user.created_quests.filter(done=True).order_by('-created')[:10],
#             'quests_joined': Quest.objects.filter(canceled=False, adventures__user=user, adventures__canceled=False)[:10]
             })


@login_required
def quest_my(request):
    """Views the quests the hero is envolved with."""
    template='herobase/quest/my.html'
    user = request.user

    created_q = Q(owner=user)
    joined_q = Q(adventures__user=user)
    quests = Quest.objects.filter(canceled=False, done=False).filter(created_q | joined_q).order_by('-created')

    return render(request, template, {'quests': quests})

def quest_my_created(request):
    """Views the quests the hero is envolved with."""
    template='herobase/quest/my.html'
    user = request.user

    return render(request, template, {
        'quests': user.created_quests.filter(canceled=False, done=False).order_by('-created'),
        }
    )
def quest_my_joined(request):
    """Views the quests the hero is envolved with."""
    template='herobase/quest/my.html'
    user = request.user

    return render(request, template, {
        'quests': Quest.objects.filter(canceled=False, done=False).filter(adventures__user=user),
        }
    )
def quest_my_done(request):
    """Views the quests the hero is envolved with."""
    template='herobase/quest/my.html'
    user = request.user

    created_q = Q(owner=user)
    joined_q = Q(adventures__user=user)
    quests = Quest.objects.exclude(canceled=False, done=False).filter(created_q | joined_q).order_by('-created')

    return render(request, template, { 'quests': quests })


@require_POST
@login_required
def owner_update_quest(request, quest_id):
    """Handle POST data for quest-actions and redirect to quest-detail-view."""
    quest = get_object_or_404(Quest, pk=quest_id)
    if not quest.owner == request.user:
        return HttpResponseForbidden("You are not the owner of this quest.")

    # start / cancel / done / document

    action = request.POST.get('action')
    try:
        if action == 'start':
            quest_livecycle.owner_quest_start(quest)
        elif action == 'cancel':
            quest_livecycle.owner_quest_cancel(quest)
        elif action == 'done':
            quest_livecycle.owner_quest_done(quest)
        elif action == 'accept_all':
            quest_livecycle.owner_accept_all(quest)
        else:
            raise ValidationError('No known action specified')
    except ValidationError as e:
        messages.error(request, e.messages[0])
    return HttpResponseRedirect(reverse('quest_detail', args=(quest.pk, )))

@require_POST
@login_required
def owner_update_hero(request, quest_id, hero_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    hero = get_object_or_404(User, pk=hero_id)

    if not quest.owner == request.user:
        return HttpResponseForbidden("You are not the owner of this quest.")

    action = request.POST.get('action')
    try:
        if action == 'accept':
            quest_livecycle.owner_hero_accept(quest, hero)
        elif action == 'reject':
            quest_livecycle.owner_hero_reject(quest, hero)
        else:
            raise ValidationError('No known action specified')
    except ValidationError as e:
        messages.error(request, e.messages[0])
    return HttpResponseRedirect(reverse('quest_detail', args=(quest.pk, )))

@require_POST
@login_required
def hero_update_quest(request, quest_id):
    """Handle POST data for adventure-actions and redirect to quest-detail-view."""
    quest = get_object_or_404(Quest, pk=quest_id)

    if quest.owner == request.user:
        raise ValidationError("Im afraid I can't let you do that.")

    action = request.POST.get('action')
    try:
        if action == 'apply':
            quest_livecycle.hero_quest_apply(quest, request.user)
        elif action == 'cancel':
            quest_livecycle.hero_quest_cancel(quest, request.user)
        else:
            raise ValidationError('No known action specified')
    except ValidationError as e:
        messages.error(request, e.messages[0])
    return HttpResponseRedirect(reverse('quest_detail', args=(quest.pk, )))

@login_required
def userprofile(request, username=None, template='herobase/userprofile/detail.html'):
    """Render Userprofile with some stats."""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    rank = UserProfile.objects.filter(experience__gt=user.get_profile().experience).count() + 1
    hero_completed_quests = []
    class_choices = dict(CLASS_CHOICES)
    color_dict = { 5: '#e8e8e8',
                   1: '#ccffa7',
                   2: '#fff9b4',
                   3: '#ffa19b',
                   4: '#bdcaff'}


    return render(request, template, {
        'user': user,
        'rank': rank,
        'completed_quest_count': user.adventures.filter(done=True).count(),
        'hero_completed_quests': mark_safe(json.dumps(hero_completed_quests)),
        # 'colors': json.dumps(color_dict),
    })


@login_required
def userprofile_edit(request):
    """Render the userprofile form and handle possible changes."""
    user = request.user
    form = UserProfileEdit(request.POST or None, instance=user.get_profile())
    if form.is_valid():
        form.save()
        messages.success(request, 'Profile successfully changed')
        return HttpResponseRedirect(reverse("userprofile_edit"))
    return render(request, 'herobase/userprofile/edit.html', {
        'form': form
    })

@login_required
def userprofile_privacy_settings(request):
    """Render another userprofile form for privacy settings saved on the userprofile."""
    user = request.user
    form = UserProfilePrivacyEdit(request.POST or None, instance=user.get_profile())
    if form.is_valid():
        form.save()
        messages.success(request, 'Privacy settings successfully changed')
        return HttpResponseRedirect('.')
    return render(request, 'herobase/userprofile/privacy_settings.html', {
        'form': form
    })

@login_required
def userprofile_skill_settings(request):
    form = UserSkillEditForm(request.POST or None, instance=request.user.selected_skills)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect('.')

    context = { 'selected': len(request.user.selected_skills.get_skills()),
                'minimum': MIN_SELECTED_SKILLS,
                'form': form,
            }
    return render(request, 'herobase/userprofile/skill_settings.html', context)

@login_required
def leader_board(request):
    """Render a view of the top heroes by rank."""
    global_board = User.objects.select_related().filter(profile__experience__gt=0).order_by('-profile__experience')[:10]
    relativ_board = []

    return render(request, "herobase/leader_board.html", {
        'global_board': global_board,
        'relativ_board': relativ_board,
    })

@login_required
def random_stats(request):
    """Some general stats"""
    user = request.user
    class_choices = dict(CLASS_CHOICES)
    color_dict = { None: "#ff0000",
                    5: '#e8e8e8',
                   1: '#ccffa7',
                   2: '#fff9b4',
                   3: '#ffa19b',
                   4: '#bdcaff'}



    hero_completed_quests = []
    colors0 = []
    open_quest_types = []
    colors1 = []
    completed_quest_types = []

    context = {
        'hero_completed_quests': hero_completed_quests,
        'open_quest_types': open_quest_types,
        'completed_quest_types': completed_quest_types,
        'colors0': colors0,
        'colors1': colors1,
        }
    for key in context:
        context[key] = mark_safe(json.dumps(list(context[key])))

    context.update({
        'quests_completed': user.adventures.filter(quest__done=True).count()
    })

    return render(request, 'herobase/stats.html', context)

def signups(request):
    """Special view for nosy developers."""
    if request.user.is_authenticated() and request.user.is_staff:
        logged_in = '\n'.join('%s: %s' % (u.last_login, u.username) for u in User.objects.order_by('-last_login')[:20])
        signed_up = '\n'.join('%s: %s' % (u.date_joined, u.username) for u in User.objects.order_by('-date_joined')[:10])
        return HttpResponse('Logged in \n%s\nJoined\n%s' % (logged_in, signed_up), mimetype='text/plain')
    else:
        raise Http404()

@require_POST
@login_required
def like_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    like, created = Like.objects.get_or_create(user=request.user, quest=quest)

    if created:
        recommender_signals.like.send(sender=request.user, quest=quest) 

    return HttpResponse(json.dumps({'success': True}), mimetype='application/json')
