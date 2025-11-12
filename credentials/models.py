from django.db import models
from profiles.models import UserProfile


class Credential(models.Model):

    class CredentialType(models.TextChoices):
        PROFESSIONAL = 'PRO', 'Profissional'
        GRADUATE = 'GRA', 'Graduado'

    class ExperienceLevel(models.TextChoices):
        JUNIOR = 'JR', 'Júnior'
        MID_LEVEL = 'PL', 'Pleno'
        SENIOR = 'SR', 'Sênior'

    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    role = models.CharField(max_length=80)
    type_credential = models.CharField(choices=CredentialType.choices)
    experience = models.CharField(choices=ExperienceLevel.choices)
    institution = models.CharField(max_length=120)
    start_date = models.DateField(help_text="Data de início")
    end_date = models.DateField(null=True, blank=True, help_text="Data de término (deixe em branco se for atual)")
    is_verified = models.BooleanField(
        default=False,
        help_text="Marque como 'True' se esta credencial foi validada pelo admin"
    )

    class Meta:
        unique_together = ('profile', 'role', 'institution')

    def __str__(self) -> str:
        return f'{self.role} em {self.institution}'
