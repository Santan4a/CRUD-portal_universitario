from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from alunos.forms import GestaoAlunoForm
from alunos.models import Aluno
from disciplinas.catalogo import disciplinas_por_curso_json
from disciplinas.models import Disciplina

from .access import get_user_role, role_required


@login_required
def portal_redirect(request):
    role = get_user_role(request.user)

    if role == 'aluno':
        return redirect('minha_area')

    if role == 'gestao':
        return redirect('dashboard_gestao')

    if role == 'professor':
        return redirect('lista_alunos')

    return redirect('login')


@role_required('gestao')
def dashboard_gestao(request):
    alunos = Aluno.objects.prefetch_related('disciplinas').order_by('-id')
    total_cursos = (
        Aluno.objects.exclude(curso='')
        .values('curso')
        .distinct()
        .count()
    )

    context = {
        'total_alunos': alunos.count(),
        'total_cursos': total_cursos,
        'total_disciplinas': Disciplina.objects.count(),
        'ultimos_alunos': alunos[:6],
    }

    return render(request, "gestao/dashboard.html", context)


@role_required('gestao')
def cadastrar_aluno_gestao(request):
    form = GestaoAlunoForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('dashboard_gestao')

    return render(
        request,
        'gestao/cadastro_aluno.html',
        {
            'form': form,
            'disciplinas_por_curso': disciplinas_por_curso_json(),
        }
    )


def contato(request):
    return render(request, 'contato.html')

def suporte(request):
    return render(request, 'suporte.html')

def politicas(request):
    return render(request, 'politicas.html')
