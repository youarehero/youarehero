# -*- coding: utf-8 -*-
"""
The Views module provide view functions, which were called by the
`url dispatcher <https://docs.djangoproject.com/en/1.4/topics/http/urls/>`_,
and aggregate some data for use in templates.
"""
import datetime
from django.contrib.auth import logout
import logging

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.comments import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site, RequestSite
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Q
from django.forms.models import model_to_dict
from django.utils.translation import ugettext as _
from django.utils import simplejson as json
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import (HttpResponseRedirect, Http404,
                         HttpResponse, HttpResponseForbidden)
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView
from heroorganization.models import Organization
from heroorganization.views import OrganizationListView
from registration.backends.default.views import RegistrationView, ActivationView
import registration.signals


from herobase.utils import is_minimum_age
from heronotification.models import Notification
from heromessage.models import Message
from herorecommend.forms import UserSkillEditForm
from herobase.forms import (QuestCreateForm, UserProfileEditForm,
                            UserProfilePrivacyForm, UserAuthenticationForm, DateOfBirthRegistrationForm, DocumentationForm)
from herobase.models import Quest, Adventure, Like, CREATE_EXPERIENCE, UserProfile, Documentation
from herorecommend.models import MIN_SELECTED_SKILLS
from registration.models import RegistrationProfile

logger = logging.getLogger('youarehero.herobase')


def quest_list_view(request, archive=False, done=False,
                    template='herobase/quest/list.html'):
    """Basic quest list, with django-filter app"""
    quests = Quest.objects.all().select_related('owner', 'owner__profile')\
                                .order_by('-created', 'pk')

    if (request.user.is_authenticated() and
            not request.user.profile.is_legal_adult()):
        quests = quests.filter(owner__profile__trusted=True)

    if not archive and not done:
        quests = quests.open()
    if done:
        quests = Quest.objects.done().select_related('owner', 'owner__profile')\
                                     .order_by('-done_time', 'pk')

    search = request.GET.get('search', '')
    if search:
        quests = quests.filter(
            Q(title__icontains=search) | Q(description__icontains=search))

    return render(request, template, {
        'quests': quests,
        'search': search,
        'done': done,
    })


class QuestUpdateView(UpdateView):
    """
    Basic Quest create view.
    This generic view-class should be refactored to a normal view function
    """
    context_object_name = "quest"
    form_class = QuestCreateForm
    model = Quest
    template_name = "herobase/quest/update.html"
    success_url = '../'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(QuestUpdateView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.owner == request.user:
            return HttpResponseForbidden(_("Only the owner can edit the quest."))
        if self.object.edit_window_expired:
            return HttpResponseForbidden(_("You can only edit quests for %s minutes.") %
                                         Quest.EDIT_WINDOW_MINUTES)
        return super(QuestUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.owner == request.user:
            return HttpResponseForbidden(_("Only the owner can edit the quest."))
        if self.object.edit_window_expired:
            return HttpResponseForbidden(_("You can only edit quests for %s minutes.") %
                                         Quest.EDIT_WINDOW_MINUTES)
        return super(QuestUpdateView, self).post(request, *args, **kwargs)


class QuestCreateView(CreateView):
    """
    Basic Quest create view.
    This generic view-class should be refactored to a normal view function
    """
    context_object_name = "quest"
    form_class = QuestCreateForm
    template_name = "herobase/quest/create.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(QuestCreateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()


    def get_form(self, form_class):
        form_kwargs = self.get_form_kwargs()
        recreate_id = self.kwargs.get('quest_id')
        if recreate_id:
            quest = Quest.objects.get(pk=recreate_id, owner=self.request.user)
            initial = model_to_dict(quest)
            for field in ('pk', 'start_date', 'expiration_date'):
                initial.pop(field, None)
            form_kwargs['initial'] = initial

        return form_class(**form_kwargs)

    def form_valid(self, form):
        if not self.request.user.profile.is_legal_adult():
            raise ValidationError("Minors are not allowed to create quests")

        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        self.object.owner.get_profile().experience += CREATE_EXPERIENCE
        self.object.owner.get_profile().save()
        return HttpResponseRedirect(self.get_success_url())


def quest_detail_view(request, quest_id):
    """Render detail template for quest, and adventure if it exists."""
    quest = get_object_or_404(
        Quest.objects.select_related('owner', 'owner__profile'),
        pk=quest_id)

    if (request.user.is_authenticated() and
            not request.user.profile.is_legal_adult() and
            not quest.owner.profile.trusted):
        return HttpResponse(
            "Minors are not allowed to view untrusted users' quests",
            status=403)

    is_owner = request.user == quest.owner
    if request.user.is_authenticated() and not is_owner:
        try:
            adventure = quest.adventures.get(
                user_id=request.user.pk,
                canceled=False)
        except Adventure.DoesNotExist:
            adventure = Adventure()
            adventure.user = request.user
            adventure.quest = quest
    else:
        adventure = None
    if is_owner:
        butler_text = _(u'Dies ist ihre Quest.')
    elif not adventure:
        butler_text = _(
            u"This quest needs heroes. "
            u"Apply now by clicking the ✓ Button on the right.")
    elif adventure.accepted:
        butler_text = _(
            u"Your application has been accepted. "
            u"Press X to withdraw your participation.")
    elif adventure.rejected:
        butler_text = _(
            u"You have applied for this quest but the owner "
            u"didn't want you to participate in it.")
    elif not adventure.accepted and not adventure.rejected:
        butler_text = _(
            u"You are currently applying for this quest. Press X to cancel."
            u" You will be notified once the creator has "
            u"decided about our participation")
    else:
        butler_text = u"Hello"

    if is_owner:
        adventures = quest.adventures.all().select_related(
            'user',
            'user__profile')
    else:
        adventures = quest.adventures.accepted().select_related(
            'user',
            'user__profile')

    quest_content_type = ContentType.objects.get_for_model(Quest)
    comments = Comment.objects.filter(
        content_type=quest_content_type,
        object_pk=quest.pk
    ).select_related('user__profile')

    hero_documentation = Documentation.objects.filter(quest=quest).exclude(user=quest.owner)
    try:
        owner_documentation = Documentation.objects.get(quest=quest, user=quest.owner)
    except Documentation.DoesNotExist:
        owner_documentation = None

    if request.user == quest.owner or request.user in quest.heroes:
        try:
            documentation = Documentation.objects.get(user=request.user, quest=quest)
        except Documentation.DoesNotExist:
            documentation = None
        documentation_form = DocumentationForm(instance=documentation)
    else:
        documentation_form = None

    context = {
        'quest': quest,
        'adventures': adventures,
        'butler_text': butler_text,
        'is_owner': is_owner,
        'documentation_form': documentation_form,
        'hero_documentation': hero_documentation,
        'owner_documentation': owner_documentation,
        'comments': comments,
        'adventure': adventure,
        'quest_url': reverse('quest_detail', args=(quest.pk,)),
    }
    return render(request, "herobase/quest/detail.html", context)


def home_view(request):
    """Proxy view for switching between the hero and the public home view"""
    if request.user.is_authenticated():
        return hero_home_view(request)
    response = render(request, "herobase/public_home.html", {
        'recently_done_quests': Quest.objects.done().order_by('-done_time')[:3],
        'form': UserAuthenticationForm()})
    response['Access-Control-Allow-Origin'] = "www.facebook.com"
    return response


@login_required
def hero_home_view(request, template='herobase/hero_home.html'):
    """the hero home is only visible for authenticated heros."""
    return render(request, template, {
        'notifications': Notification.unread_for_user(request.user),
    })


@login_required
def quest_my(request):
    """Views the quests the hero is envolved with."""
    template = 'herobase/quest/my.html'
    user = request.user

    # Quests
    created_q = Q(owner=user)
    joined_q = Q(adventures__user=user, adventures__canceled=False)

    quests_all = Quest.objects.filter(
        canceled=False,
        done=False
    ).filter(
        created_q | joined_q
    ).order_by('-created').distinct().select_related('owner', 'owner__profile')

    quests_created = user.created_quests.filter(
                canceled=False,
                done=False
            ).order_by('-created').select_related('owner', 'owner__profile')

    quests_joined = Quest.objects.filter(
                canceled=False,
                done=False
            ).filter(
                adventures__user=user,
                adventures__canceled=False
            ).select_related('owner', 'owner__profile')

    created_q = Q(owner=user)
    joined_q = Q(adventures__user=user)
    quests_done = Quest.objects.exclude(
        canceled=False,
        done=False
    ).filter(
        created_q | joined_q
    ).order_by('-created').select_related('owner', 'owner__profile')

    return render(request, template, {
        'user': user,
        'rank': user.get_profile().rank,
        'completed_quest_count': user.adventures.filter(done=True).count(),
        'quests_all': quests_all,
        'quests_created': quests_created,
        'quests_joined': quests_joined,
        'quests_done': quests_done,
    })


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
            quest.state.start()
        elif action == 'cancel':
            quest.state.cancel()
        elif action == 'done':
            quest.state.done()
        elif action == 'accept_all':
            quest.state.accept_all()
        else:
            raise ValidationError('No known action specified')
    except ValidationError as e:
        messages.error(request, e.messages[0])
    return HttpResponseRedirect(reverse('quest_detail', args=(quest.pk, )))


@require_POST
@login_required
def quest_document(request, pk):
    quest = get_object_or_404(Quest, pk=pk)
    if request.user != quest.owner and request.user not in quest.heroes:
        return HttpResponseForbidden()

    try:
        documentation = Documentation.objects.get(quest=quest, user=request.user)
    except Documentation.DoesNotExist:
        documentation = None

    form = DocumentationForm(request.POST, request.FILES, instance=documentation)
    if form.is_valid():
        documentation = form.save(commit=False)
        documentation.quest = quest
        documentation.user = request.user
        documentation.save()

    return HttpResponseRedirect(quest.get_absolute_url())


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
            quest.adventure_state(hero).accept()
        elif action == 'reject':
            quest.adventure_state(hero).reject()
        else:
            raise ValidationError('No known action specified')
    except ValidationError as e:
        messages.error(request, e.messages[0])
    return HttpResponseRedirect(reverse('quest_detail', args=(quest.pk, )))


@require_POST
@login_required
def hero_update_quest(request, quest_id):
    """
    Handle POST data for adventure-actions and redirect to quest-detail-view.
    """
    quest = get_object_or_404(Quest, pk=quest_id)

    if quest.owner == request.user:
        raise ValidationError("Im afraid I can't let you do that.")

    if not request.user.profile.is_legal_adult()\
            and not quest.owner.profile.trusted:
        return HttpResponse(
            "Minors are not allowed to apply to untrusted users' quests",
            status=403)

    action = request.POST.get('action')
    try:
        if action == 'apply':
            quest.adventure_state(request.user).apply()
        elif action == 'cancel':
            quest.adventure_state(request.user).cancel()
        else:
            raise ValidationError('No known action specified')
    except ValidationError as e:
        messages.error(request, e.messages[0])
    return HttpResponseRedirect(reverse('quest_detail', args=(quest.pk, )))


@login_required
def userprofile(request, username=None,
                template='herobase/userprofile/detail.html'):
    """Render Userprofile with some stats."""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    try:
        organization = user.organization
        return HttpResponseRedirect(organization.get_absolute_url())
    except ObjectDoesNotExist:
        pass

    # Quests
    created_q = Q(owner=user)
    joined_q = Q(adventures__user=user, adventures__canceled=False)

    quests_all = Quest.objects.filter(
        canceled=False,
        done=False
    ).filter(
        created_q | joined_q
    ).order_by('-created').distinct().select_related('owner', 'owner__profile')

    quests_created = user.created_quests.filter(
                canceled=False,
                done=False
            ).order_by('-created').select_related('owner', 'owner__profile')

    quests_joined = Quest.objects.filter(
                canceled=False,
                done=False
            ).filter(
                adventures__user=user,
                adventures__canceled=False
            ).select_related('owner', 'owner__profile')

    created_q = Q(owner=user)
    joined_q = Q(adventures__user=user)
    quests_done = Quest.objects.exclude(
        canceled=False,
        done=False
    ).filter(
        created_q | joined_q
    ).order_by('-created').select_related('owner', 'owner__profile')

    return render(request, template, {
        'user': user,
        'rank': user.get_profile().rank,
        'completed_quest_count': user.adventures.filter(done=True).count(),
        'quests_all': quests_all,
        'quests_created': quests_created,
        'quests_joined': quests_joined,
        'quests_done': quests_done,
    })


@login_required
def userprofile_edit(request):
    """Render the userprofile form and handle possible changes."""
    user = request.user
    if Organization.objects.filter(user=request.user).exists():
        return HttpResponseRedirect(reverse("organization_update"))
    form = UserProfileEditForm(request.POST or None, request.FILES or None, instance=user.get_profile())
    first_login = bool(request.GET.get('first_login'))
    if form.is_valid():
        form.save()
        messages.success(request, _(u'Profile successfully changed'))
        if first_login:
            return HttpResponseRedirect(reverse("home"))
        return HttpResponseRedirect(reverse("userprofile_edit"))
    return render(request, 'herobase/userprofile/edit.html', {
        'form': form,
        'first_login': first_login,
    })

@login_required
def userprofile_delete(request):
    """Remove all Information of a User and set her inactive."""
    if request.method == 'POST':
        user = request.user
        user.username = "Held in Rente %s" % user.pk
        user.first_name = ''
        user.last_name = ''
        user.email = ''
        user.is_active = False
        user.is_staff = False
        user.is_superuser = False
        user.save()

        profile = user.get_profile()
        profile.location = ''
        profile.sex = 3
        profile.date_of_birth = datetime.date.fromtimestamp(0)
        profile.team = ''
        profile.public_location = False
        profile.about = ''
        profile.receive_system_email = False
        profile.receive_private_email = False
        profile.uploaded_image = None
        profile.image = None
        profile.save()

        logout(request)

        return HttpResponseRedirect(reverse('home'))
    else:
        return render(request, "herobase/userprofile/confirm_delete.html", {})

@login_required
def userprofile_privacy_settings(request):
    """
    Render another userprofile form for privacy settings
    saved on the userprofile.
    """
    user = request.user
    form = UserProfilePrivacyForm(
        request.POST or None,
        instance=user.get_profile())
    if form.is_valid():
        form.save()
        messages.success(request, _(u'Privacy settings successfully changed'))
        return HttpResponseRedirect('.')
    return render(request, 'herobase/userprofile/privacy_settings.html', {
        'form': form
    })


@login_required
def userprofile_skill_settings(request):
    form = UserSkillEditForm(
        request.POST or None,
        instance=request.user.selected_skills)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect('.')

    context = {
        'selected': len(request.user.selected_skills.get_skills()),
        'minimum': MIN_SELECTED_SKILLS,
        'form': form,
    }
    return render(request, 'herobase/userprofile/skill_settings.html', context)


@login_required
def leader_board(request):
    """Render a view of the top heroes by rank."""
    global_board = User.objects.select_related('profile').filter(
        profile__experience__gt=0
    ).order_by('-profile__experience')[:10]
    relativ_board = []

    return render(request, "herobase/leader_board.html", {
        'global_board': global_board,
        'relativ_board': relativ_board,
    })


def signups(request):
    """Special view for nosy developers."""
    if request.user.is_authenticated() and request.user.is_staff:
        logged_in = '\n'.join(
            '%s: %s' % (u.last_login, u.username)
            for u in User.objects.order_by('-last_login')[:20])
        signed_up = '\n'.join(
            '%s: %s' % (u.date_joined, u.username)
            for u in User.objects.order_by('-date_joined')[:10])
        return HttpResponse(
            'Logged in \n%s\nJoined\n%s' % (logged_in, signed_up),
            mimetype='text/plain')
    else:
        raise Http404()


@require_POST
@login_required
def like_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    like, created = Like.objects.get_or_create(user=request.user, quest=quest)

    if not request.user.profile.is_legal_adult()\
            and not quest.owner.profile.trusted:
        return HttpResponse(
            "Minors are not allowed to like untrusted users' quests",
            status=403)

    # TODO: XP
    # if created:
        # recommender_signals.like.send(sender=request.user, quest=quest)

    return HttpResponse(
        json.dumps(
            {'success': True, 'likes_count': quest.likes_count}
        ),
        mimetype='application/json')


def team(request, team_name):
    users = User.objects.select_related(
        'profile'
    ).filter(profile__team=team_name)

    if not users:
        raise Http404()

    return render(
        request,
        "herobase/team.html",
        {
            'team_name': team_name,
            'users': users
        })


class AgeRequiredRegistrationView(RegistrationView):
    form_class = DateOfBirthRegistrationForm

    def register(self, request, **cleaned_data):
        username = cleaned_data['username']
        email = cleaned_data['email']
        password = cleaned_data['password1']
        date_of_birth = cleaned_data['date_of_birth']

        if not is_minimum_age(date_of_birth):
            return "BELOW_MINIMUM_AGE"

        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = RegistrationProfile.objects.create_inactive_user(username, email,
                                                                    password, site)
        registration.signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)

        profile, created = UserProfile.objects.get_or_create(
            user=new_user,
        )
        profile.date_of_birth = date_of_birth
        profile.save()
        return new_user

    def get_success_url(self, request, user):
        if user == "BELOW_MINIMUM_AGE":
            return reverse("registration_below_minimum_age")
        return super(AgeRequiredRegistrationView, self).get_success_url(request, user)


class RedirectToProfileActivationView(ActivationView):
    def get_success_url(self, request, user):
        return reverse("userprofile_edit") + "?first_login=True"
