from django.db import models
from profiles.models import UserProfile
from technologies.models import Technology


class Question(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Descrição do problema (suporta Markdown)")
    is_published = models.BooleanField(default=True)
    is_solutioned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='author')
    technologies = models.ManyToManyField(Technology, related_name='question_tags')
    likes = models.ManyToManyField(UserProfile, related_name='question_likes', null=True, blank=True)

    def __str__(self) -> str:
        return self.title
