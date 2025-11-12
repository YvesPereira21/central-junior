from django.contrib import admin
from credentials.models import Credential


@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = ('pk', 'profile', 'role', 'type_credential', 'experience',
                    'institution', 'start_date', 'end_date', 'is_verified')
