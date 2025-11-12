from django.contrib import admin
from technologies.models import Technology


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'color', 'logo', 'prism_lang')
