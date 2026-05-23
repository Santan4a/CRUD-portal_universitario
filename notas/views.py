from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404

from alunos.models import Aluno
from .models import Nota
from .forms import NotaForm
from users.access import is_aluno, is_gestao, is_professor, role_required


def disciplinas_por_aluno_json():
    alunos = Aluno.objects.prefetch_related('disciplinas').order_by('nome')
    dados = {}

    for aluno in alunos:
        disciplinas = sorted(
            aluno.disciplinas.all(),
            key=lambda disciplina: (disciplina.nome, disciplina.codigo)
        )
        dados[str(aluno.id)] = [
            {
                'id': disciplina.id,
                'nome': disciplina.nome,
                'codigo': disciplina.codigo,
            }
            for disciplina in disciplinas
        ]

    return dados


# LISTAR
@login_required
def lista_notas(request):
    can_manage = is_professor(request.user) or is_gestao(request.user)
    can_delete = is_professor(request.user)

    if is_aluno(request.user):
        aluno = getattr(request.user, 'aluno', None)
        notas = Nota.objects.none()

        if aluno:
            notas = Nota.objects.filter(aluno=aluno)
            disciplina_ids = list(aluno.disciplinas.values_list('id', flat=True))

            if disciplina_ids:
                notas = notas.filter(disciplina_id__in=disciplina_ids)
    elif can_manage:
        notas = Nota.objects.all()
    else:
        raise PermissionDenied

    return render(
        request,
        'notas/lista.html',
        {
            'notas': notas.select_related('aluno', 'disciplina'),
            'can_manage': can_manage,
            'can_delete': can_delete,
        }
    )


# CRIAR
@role_required('professor', 'gestao')
def criar_nota(request):
    form = NotaForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('lista_notas')

    return render(
        request,
        'notas/form.html',
        {
            'form': form,
            'disciplinas_por_aluno': disciplinas_por_aluno_json(),
        }
    )


# EDITAR
@role_required('professor', 'gestao')
def editar_nota(request, id):
    nota = get_object_or_404(Nota, id=id)
    form = NotaForm(request.POST or None, instance=nota)

    if form.is_valid():
        form.save()
        return redirect('lista_notas')

    return render(
        request,
        'notas/form.html',
        {
            'form': form,
            'disciplinas_por_aluno': disciplinas_por_aluno_json(),
        }
    )


# DELETAR
@role_required('professor')
def deletar_nota(request, id):
    nota = get_object_or_404(Nota, id=id)

    if request.method == 'POST':
        nota.delete()
        return redirect('lista_notas')

    return render(request, 'notas/confirmar_exclusao.html', {'nota': nota})
