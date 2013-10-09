# Create your views here.
from django.shortcuts import render
from heroachievements import achievements


def achievement_list(request):
    return render(request, "heroachievements/achievement_list.html", {
        'achievements': achievements.registry.values(),
    })