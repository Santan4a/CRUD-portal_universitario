from django.contrib import admin

from users.access import is_aluno, is_gestao, is_professor
from .models import Nota


@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'disciplina', 'nota1', 'nota2')
    list_filter = ('disciplina',)
    search_fields = ('aluno__nome', 'aluno__matricula', 'disciplina__nome')

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or is_gestao(request.user) or is_aluno(request.user) or is_professor(request.user)

    def has_add_permission(self, request):
        return request.user.is_superuser or is_gestao(request.user) or is_professor(request.user)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or is_gestao(request.user) or is_professor(request.user)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or is_gestao(request.user) or is_professor(request.user)
