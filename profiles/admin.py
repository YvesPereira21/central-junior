from django.contrib import admin
from profiles.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'avatar', 'expertise',
                    'level', 'reputation_score', 'is_professional')
