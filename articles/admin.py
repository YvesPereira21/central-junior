from django.contrib import admin
from articles.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'author', 'slug', 'content', 'created_at')
    filter_vertical = ('likes', 'technologies')
