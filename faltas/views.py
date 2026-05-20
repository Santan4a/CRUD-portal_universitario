from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FaltaForm
from .models import Falta
from users.access import is_aluno, is_professor, role_required


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
    elif is_professor(request.user):
        faltas = Falta.objects.all()
    else:
        raise PermissionDenied

    return render(
        request,
        'faltas/lista.html',
        {
            'faltas': faltas.select_related('aluno', 'disciplina'),
            'can_manage': is_professor(request.user),
        }
    )


@role_required('professor')
def criar_falta(request):
    form = FaltaForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('lista_faltas')

    return render(request, 'faltas/form.html', {'form': form})


@role_required('professor')
def editar_falta(request, id):
    falta = get_object_or_404(Falta, id=id)
    form = FaltaForm(request.POST or None, instance=falta)

    if form.is_valid():
        form.save()
        return redirect('lista_faltas')

    return render(request, 'faltas/form.html', {'form': form})


@role_required('professor')
def excluir_falta(request, id):
    falta = get_object_or_404(Falta, id=id)

    if request.method == 'POST':
        falta.delete()
        return redirect('lista_faltas')

    return render(request, 'faltas/confirmar_exclusao.html', {'falta': falta})
