from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from users.access import get_professor_discipline_ids, is_aluno, is_professor
from .models import Cronograma


@login_required
def grade_horarios(request):

    cronogramas = Cronograma.objects.select_related(
        'disciplina'
    ).all()

    if is_aluno(request.user):
        aluno = getattr(request.user, 'aluno', None)
        disciplina_ids = aluno.disciplinas.values_list('id', flat=True) if aluno else []
        cronogramas = cronogramas.filter(disciplina_id__in=disciplina_ids)

        if aluno and aluno.turno:
            cronogramas = cronogramas.filter(turno=aluno.turno)
    elif is_professor(request.user):
        cronogramas = cronogramas.filter(
            disciplina_id__in=get_professor_discipline_ids(request.user)
        )

    contexto = {
        'cronogramas': cronogramas.order_by(
            'dia_semana',
            'turno',
            'horario_inicio',
            'disciplina__nome',
        )
    }

    return render(
        request,
        'cronograma/grade.html',
        contexto
    )
