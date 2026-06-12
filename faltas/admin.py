from django.contrib import admin

from users.access import is_aluno, is_gestao, is_professor
from .models import Chamada, Falta, LimiteFaltas, PresencaChamada


class ProfessorWriteAdminMixin:
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or is_gestao(request.user) or is_aluno(request.user) or is_professor(request.user)

    def has_add_permission(self, request):
        return request.user.is_superuser or is_gestao(request.user) or is_professor(request.user)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or is_gestao(request.user) or is_professor(request.user)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or is_gestao(request.user) or is_professor(request.user)


@admin.register(Falta)
class FaltaAdmin(ProfessorWriteAdminMixin, admin.ModelAdmin):
    list_display = ('aluno', 'disciplina', 'data', 'justificada', 'criado_em')
    list_filter = ('justificada', 'data', 'disciplina')
    search_fields = ('aluno__nome', 'aluno__matricula', 'disciplina__nome')
    date_hierarchy = 'data'
    ordering = ('-data',)


@admin.register(Chamada)
class ChamadaAdmin(ProfessorWriteAdminMixin, admin.ModelAdmin):
    list_display = ('disciplina', 'data', 'professor', 'realizado_em')
    list_filter = ('disciplina', 'data')
    search_fields = ('disciplina__nome', 'professor__username')
    date_hierarchy = 'data'
    ordering = ('-data',)


@admin.register(PresencaChamada)
class PresencaChamadaAdmin(ProfessorWriteAdminMixin, admin.ModelAdmin):
    list_display = ('chamada', 'aluno', 'presente')
    list_filter = ('presente', 'chamada__disciplina')
    search_fields = ('aluno__nome', 'aluno__matricula', 'chamada__disciplina__nome')
    raw_id_fields = ('chamada', 'aluno')


@admin.register(LimiteFaltas)
class LimiteFaltasAdmin(ProfessorWriteAdminMixin, admin.ModelAdmin):
    list_display = ('disciplina', 'carga_horaria_total', 'percentual_maximo', 'faltas_maximas')
    list_filter = ('disciplina',)
    search_fields = ('disciplina__nome',)
    readonly_fields = ('faltas_maximas',)
