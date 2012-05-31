import autocomplete_light
from django.contrib.auth.models import User

autocomplete_light.register(User, search_field='username', placeholder='Username')
