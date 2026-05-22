from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'matricula')
    search_fields = ('user__username', 'user__email', 'matricula')
    list_filter = ('role',)
    readonly_fields = ('matricula',)