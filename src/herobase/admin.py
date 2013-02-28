from django.contrib import admin
from herobase.models import UserProfile, Quest, Adventure, Like
from heromessage.models import Message
from herorecommend.models import UserCombinedProfile,UserRatingProfile, UserSelectionProfile, SkillBase, QuestProfile

class UserProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Quest)
admin.site.register(Adventure)
admin.site.register(Message)
admin.site.register(Like)
admin.site.register(UserCombinedProfile)
admin.site.register(QuestProfile)