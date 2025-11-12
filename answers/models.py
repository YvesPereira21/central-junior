from django.db import models
from profiles.models import UserProfile
from questions.models import Question


class Answer(models.Model):
    content = models.TextField(help_text='Uma resposta também pode inserir markdown')
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='answer_author')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    upvotes = models.ManyToManyField(UserProfile, related_name='upvote', null=True, blank=True)

    def __str__(self) -> str:
        return f'Resposta de {self.author.user.first_name}, no dia {self.created_at}'
