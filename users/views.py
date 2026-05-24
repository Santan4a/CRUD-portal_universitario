from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import PermissionDenied

from alunos.forms import GestaoAlunoForm
from users.forms import GestaoUsuarioForm
from users.utils import gerar_email_institucional, gerar_senha_inicial_aleatoria, gerar_usuario_aluno_unico, gerar_usuario_professor_unico
from alunos.models import Aluno
from disciplinas.catalogo import disciplinas_por_curso_json
from disciplinas.models import Disciplina

from .access import get_user_role, has_screen_access, manage_screen_required
from .models import Profile


@login_required
def portal_redirect(request):
    role = get_user_role(request.user)

    if role == 'aluno':
        return redirect('minha_area')

    if has_screen_access(request.user, Profile.SCREEN_GESTAO):
        return redirect('dashboard_gestao')

    if has_screen_access(request.user, Profile.SCREEN_ALUNOS):
        return redirect('lista_alunos')

    if has_screen_access(request.user, Profile.SCREEN_NOTAS):
        return redirect('lista_notas')

    if has_screen_access(request.user, Profile.SCREEN_FALTAS):
        return redirect('lista_faltas')

    if has_screen_access(request.user, Profile.SCREEN_DISCIPLINAS):
        return redirect('lista_disciplinas')

    if role == 'superuser':
        return redirect('/admin/')

    raise PermissionDenied("Usuário sem perfil válido.")


@manage_screen_required(Profile.SCREEN_GESTAO)
def dashboard_gestao(request):
    alunos = Aluno.objects.prefetch_related('disciplinas').order_by('-id')
    professores = (
        Profile.objects.filter(role=Profile.ROLE_PROFESSOR)
        .select_related('user')
        .prefetch_related('disciplinas')
        .order_by('-id')
    )
    total_cursos = (
        Aluno.objects.exclude(curso='')
        .values('curso')
        .distinct()
        .count()
    )

    context = {
        'total_alunos': alunos.count(),
        'total_professores': professores.count(),
        'total_cursos': total_cursos,
        'total_disciplinas': Disciplina.objects.count(),
        'alunos': alunos,
        'professores': professores,
    }

    return render(request, "gestao/dashboard.html", context)


@manage_screen_required(Profile.SCREEN_GESTAO)
def cadastrar_aluno_gestao(request):
    if request.method == 'POST':
        senha_inicial = request.session.get(
            'senha_inicial_cadastro_usuario'
        ) or gerar_senha_inicial_aleatoria()
    else:
        senha_inicial = gerar_senha_inicial_aleatoria()
        request.session['senha_inicial_cadastro_usuario'] = senha_inicial

    form = GestaoUsuarioForm(
        request.POST or None,
        initial_password=senha_inicial,
    )
    proximo_usuario_professor = gerar_usuario_professor_unico(User, Profile)

    if form.is_valid():
        form.save()
        request.session.pop('senha_inicial_cadastro_usuario', None)
        return redirect('dashboard_gestao')

    return render(
        request,
        'gestao/cadastro_aluno.html',
        {
            'form': form,
            'form_title': 'Cadastrar usuário',
            'submit_label': 'Salvar usuário',
            'disciplinas_por_curso': disciplinas_por_curso_json(),
            'proximo_usuario_aluno': gerar_usuario_aluno_unico(User, Profile, Aluno),
            'proximo_usuario_professor': proximo_usuario_professor,
            'email_institucional_professor': gerar_email_institucional(proximo_usuario_professor),
            'senha_inicial_aleatoria': senha_inicial,
        }
    )


@manage_screen_required(Profile.SCREEN_GESTAO)
def editar_aluno_gestao(request, id):
    aluno = get_object_or_404(Aluno, id=id)
    form = GestaoAlunoForm(request.POST or None, instance=aluno)

    if form.is_valid():
        form.save()
        return redirect('dashboard_gestao')

    return render(
        request,
        'gestao/cadastro_aluno.html',
        {
            'aluno': aluno,
            'form': form,
            'form_title': 'Editar aluno',
            'submit_label': 'Salvar alterações',
            'disciplinas_por_curso': disciplinas_por_curso_json(),
        }
    )


def contato(request):
    return render(request, 'contato.html')


def suporte(request):
    return render(request, 'suporte.html')


def politicas(request):
    return render(request, 'politicas.html')

@manage_screen_required(Profile.SCREEN_GESTAO)
def excluir_aluno_gestao(request, id):
    aluno = get_object_or_404(Aluno, id=id)

    if request.method == 'POST':
        aluno.delete()
        return redirect('dashboard_gestao')

    return render(
        request,
        'gestao/confirmar_exclusao.html',
        {'aluno': aluno}
    )