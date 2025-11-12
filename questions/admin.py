from django.contrib import admin
from questions.models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'title', 'content', 'is_published', 'is_solutioned', 'created_at', 'profile']
    filter_vertical = ('technologies', 'likes')
