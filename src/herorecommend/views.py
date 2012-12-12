# Create your views here.
from random import randint
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from herobase.models import Quest
from herorecommend import recommend_top 


def recommend(request):
    user = User.objects.get(pk=randint(104,104))
    quests = recommend_top(user, 4)
#    paginator = Paginator(quests, 10)
#    page = paginator.page(1)
    page = {'object_list': quests}
    return render(request, 'herorecommend/benchmark.html', {'user': user, 'page': page})


@require_POST
def rate(request, quest_id, rating):
    quest = get_object_or_404(Quest, pk=quest_id)
    rating = float(rating) / 10.0

    quest_rating, created = quest.questrating_set.get_or_create(user=request.user)
    quest_rating.rating = rating

    quest_rating.save()
    return HttpResponse("Done")
