from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField()
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True)
    expertise = models.TextField()
    level = models.CharField(max_length=40, default='Iniciante', blank=True)
    reputation_score = models.IntegerField(default=0)
    is_professional = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'
