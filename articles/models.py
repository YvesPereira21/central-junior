from django.db import models
from profiles.models import UserProfile
from technologies.models import Technology


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    content = models.TextField(help_text="Corpo completo do artigo (suporta Markdown e snippets '```python')")    
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='article_author')
    technologies = models.ManyToManyField(Technology, related_name='article_tags')
    likes = models.ManyToManyField(UserProfile, related_name='article_likes')

    def __str__(self) -> str:
        return self.title
