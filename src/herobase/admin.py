from django.contrib import admin
from herobase.models import UserProfile, Quest, Adventure
from heromessage.models import Message


class UserProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Quest)
admin.site.register(Adventure)
admin.site.register(Message)