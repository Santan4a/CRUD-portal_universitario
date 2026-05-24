from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from .models import Disciplina
from .forms import DisciplinaForm
from users.access import can_manage_screen, has_screen_access, is_aluno, manage_screen_required
from users.models import Profile


@login_required
def lista_disciplinas(request):
    if is_aluno(request.user):
        aluno = getattr(request.user, 'aluno', None)
        disciplinas = aluno.disciplinas.all() if aluno else Disciplina.objects.none()
        return render(
            request,
            'disciplinas/lista.html',
            {
                'disciplinas': disciplinas,
                'can_manage': False,
            }
        )

    elif can_manage_screen(request.user, Profile.SCREEN_DISCIPLINAS):
        disciplinas = Disciplina.objects.all()
        return render(
            request,
            'disciplinas/lista.html',
            {
                'disciplinas': disciplinas,
                'can_manage': True,
            }
        )

    elif has_screen_access(request.user, Profile.SCREEN_DISCIPLINAS):
        return render(
            request,
            'disciplinas/lista.html',
            {
                'disciplinas': Disciplina.objects.none(),
                'can_manage': False,
            }
        )

    else:
        raise PermissionDenied


@manage_screen_required(Profile.SCREEN_DISCIPLINAS)
def criar_disciplina(request):
    form = DisciplinaForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('lista_disciplinas')

    return render(
        request,
        'disciplinas/form.html',
        {
            'form': form
        }
    )


@manage_screen_required(Profile.SCREEN_DISCIPLINAS)
def editar_disciplina(request, id):
    disciplina = get_object_or_404(Disciplina, id=id)
    form = DisciplinaForm(request.POST or None, instance=disciplina)

    if form.is_valid():
        form.save()
        return redirect('lista_disciplinas')

    return render(
        request,
        'disciplinas/form.html',
        {
            'form': form
        }
    )


@manage_screen_required(Profile.SCREEN_DISCIPLINAS)
def excluir_disciplina(request, id):
    disciplina = get_object_or_404(Disciplina, id=id)

    if request.method == 'POST':
        disciplina.delete()
        return redirect('lista_disciplinas')

    return render(
        request,
        'disciplinas/confirmar_exclusao.html',
        {
            'disciplina': disciplina
        }
    )