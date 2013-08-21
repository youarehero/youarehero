import autocomplete_light
from django.contrib.auth.models import User
from herobase.models import UserProfile

autocomplete_light.register(User, search_fields=['^username'], autocomplete_js_attributes={'placeholder':'Username'})

class TeamAutocomplete(autocomplete_light.AutocompleteListBase):
    choices = [entry['team'] for entry in UserProfile.objects.values('team').exclude(team="").distinct()]
    autocomplete_js_attributes = {'placeholder': 'Team name'}
autocomplete_light.register(TeamAutocomplete)
