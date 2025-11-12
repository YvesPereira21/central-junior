from django.contrib import admin
from answers.models import Answer


@admin.register(Answer)
class AnswerModelAdmin(admin.ModelAdmin):
    list_display = ('pk', 'content', 'is_accepted', 'created_at', 'author', 'question')
    filter_vertical = ('upvotes',)
