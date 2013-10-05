# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import ListView
from herobase.forms import QuestCreateForm
from herobase.models import Quest
from heroorganization.forms import OrganizationForm
from heroorganization.models import Organization


class OrganizationListView(ListView):
    slug_url_kwarg = 'name'
    slug_field = 'user__username'
    model = Organization
    template_name = "heroorganization/organization_list.html"


class OrganizationDetailView(DetailView):
    slug_url_kwarg = 'name'
    slug_field = 'user__username'
    model = Organization
    template_name = "heroorganization/organization_detail.html"


@login_required
def organization_update_view(request):
    try:
        organization = Organization.objects.get(user=request.user)
        profile = request.user.get_profile()
    except Organization.DoesNotExist:
        return HttpResponseForbidden()

    form = OrganizationForm(request.POST or None, request.FILES or None, initial={
        'about': profile.about,
    })
    if form.is_valid():
        data = form.cleaned_data
        if data['image']:
            profile.uploaded_image = data['image']
        profile.about = data['about']
        profile.save()
        return HttpResponseRedirect(reverse("organization_update"))

    return render(request, 'heroorganization/organization_update.html', {
        'form': form,
        'organization': organization,
    })