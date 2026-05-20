from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404

from .models import Nota
from .forms import NotaForm
from users.access import is_aluno, is_professor, role_required


# LISTAR
@login_required
def lista_notas(request):
    if is_aluno(request.user):
        aluno = getattr(request.user, 'aluno', None)
        notas = Nota.objects.none()

        if aluno:
            notas = Nota.objects.filter(aluno=aluno)
            disciplina_ids = list(aluno.disciplinas.values_list('id', flat=True))

            if disciplina_ids:
                notas = notas.filter(disciplina_id__in=disciplina_ids)
    elif is_professor(request.user):
        notas = Nota.objects.all()
    else:
        raise PermissionDenied

    return render(
        request,
        'notas/lista.html',
        {
            'notas': notas.select_related('aluno', 'disciplina'),
            'can_manage': is_professor(request.user),
        }
    )


# CRIAR
@role_required('professor')
def criar_nota(request):
    form = NotaForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('lista_notas')

    return render(request, 'notas/form.html', {'form': form})


# EDITAR
@role_required('professor')
def editar_nota(request, id):
    nota = get_object_or_404(Nota, id=id)
    form = NotaForm(request.POST or None, instance=nota)

    if form.is_valid():
        form.save()
        return redirect('lista_notas')

    return render(request, 'notas/form.html', {'form': form})


# DELETAR
@role_required('professor')
def deletar_nota(request, id):
    nota = get_object_or_404(Nota, id=id)

    if request.method == 'POST':
        nota.delete()
        return redirect('lista_notas')

    return render(request, 'notas/confirmar_exclusao.html', {'nota': nota})
