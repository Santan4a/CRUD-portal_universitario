from django.shortcuts import render

from .models import Cronograma


def grade_horarios(request):

    cronogramas = Cronograma.objects.select_related(
        'disciplina'
    ).all()

    contexto = {
        'cronogramas': cronogramas
    }

    return render(
        request,
        'cronograma/grade.html',
        contexto
    )