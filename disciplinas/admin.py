from django.contrib import admin

from users.access import is_aluno, is_gestao, is_professor
from .models import Disciplina


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo')
    search_fields = ('nome', 'codigo')

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or is_gestao(request.user) or is_aluno(request.user) or is_professor(request.user)

    def has_add_permission(self, request):
        return request.user.is_superuser or is_gestao(request.user) or is_professor(request.user)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or is_gestao(request.user) or is_professor(request.user)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or is_gestao(request.user) or is_professor(request.user)
