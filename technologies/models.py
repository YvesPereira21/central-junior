from django.db import models


class Technology(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#5e6e7d", help_text="Cor do 'badge' (Hex). Sempre usado se não houver logo.")
    logo = models.ImageField(upload_to='tech_logos/', null=True, blank=True, help_text="Logo da tecnologia (opcional).")
    prism_lang = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ('name', 'slug', 'logo')

    def __str__(self) -> str:
        return self.name
