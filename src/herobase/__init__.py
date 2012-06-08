# hack : change the django auth user defaults
from django.contrib.auth.models import User
try:
    User._meta.get_field_by_name('email')[0]._unique = True
    User._meta.get_field_by_name('username')[0]._length = 75
except:
    pass