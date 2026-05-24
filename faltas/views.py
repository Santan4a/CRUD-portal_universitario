from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FaltaForm
from .models import Falta
from users.access import can_manage_screen, has_screen_access, is_aluno, manage_screen_required
from users.models import Profile


@login_required
def lista_faltas(request):
    if is_aluno(request.user):
        aluno = getattr(request.user, 'aluno', None)
        faltas = Falta.objects.none()

        if aluno:
            faltas = Falta.objects.filter(aluno=aluno)
            disciplina_ids = list(aluno.disciplinas.values_list('id', flat=True))

            if disciplina_ids:
                faltas = faltas.filter(disciplina_id__in=disciplina_ids)
    elif can_manage_screen(request.user, Profile.SCREEN_FALTAS):
        faltas = Falta.objects.all()
    elif has_screen_access(request.user, Profile.SCREEN_FALTAS):
        faltas = Falta.objects.none()
    else:
        raise PermissionDenied

    return render(
        request,
        'faltas/lista.html',
        {
            'faltas': faltas.select_related('aluno', 'disciplina'),
            'can_manage': can_manage_screen(request.user, Profile.SCREEN_FALTAS),
        }
    )


@manage_screen_required(Profile.SCREEN_FALTAS)
def criar_falta(request):
    form = FaltaForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('lista_faltas')

    return render(request, 'faltas/form.html', {'form': form})


@manage_screen_required(Profile.SCREEN_FALTAS)
def editar_falta(request, id):
    falta = get_object_or_404(Falta, id=id)
    form = FaltaForm(request.POST or None, instance=falta)

    if form.is_valid():
        form.save()
        return redirect('lista_faltas')

    return render(request, 'faltas/form.html', {'form': form})


@manage_screen_required(Profile.SCREEN_FALTAS)
def excluir_falta(request, id):
    falta = get_object_or_404(Falta, id=id)

    if request.method == 'POST':
        falta.delete()
        return redirect('lista_faltas')

    return render(request, 'faltas/confirmar_exclusao.html', {'falta': falta})
