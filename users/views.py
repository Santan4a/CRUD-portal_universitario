import logging
from smtplib import SMTPAuthenticationError

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from alunos.forms import GestaoAlunoForm
from alunos.models import Aluno
from disciplinas.catalogo import disciplinas_por_curso_json
from users.emails import (
    enviar_credenciais_acesso_aluno,
    enviar_credenciais_acesso_professor,
)
from users.forms import GestaoGestorForm, GestaoProfessorForm, GestaoUsuarioForm
from users.utils import (
    gerar_email_institucional,
    gerar_senha_inicial_aleatoria,
    gerar_usuario_aluno_unico,
    gerar_usuario_professor_unico,
)

from .access import get_user_role, has_screen_access, manage_screen_required
from .models import Profile


logger = logging.getLogger(__name__)


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
    alunos_base = (
        Aluno.objects.select_related('user')
        .prefetch_related('disciplinas')
        .order_by('-id')
    )
    professores_base = (
        Profile.objects.filter(role=Profile.ROLE_PROFESSOR)
        .select_related('user')
        .prefetch_related('disciplinas')
        .order_by('-id')
    )
    gestores_base = (
        Profile.objects.filter(role=Profile.ROLE_GESTAO)
        .select_related('user')
        .order_by('-id')
    )

    query = request.GET.get('q', '').strip()
    tipo_ativo = request.GET.get('tipo', 'todos')
    tipos_validos = {'todos', 'alunos', 'professores', 'gestao'}
    if tipo_ativo not in tipos_validos:
        tipo_ativo = 'todos'

    alunos = alunos_base
    professores = professores_base
    gestores = gestores_base

    if query:
        alunos = alunos.filter(
            Q(nome__icontains=query)
            | Q(matricula__icontains=query)
            | Q(curso__icontains=query)
            | Q(turno__icontains=query)
            | Q(user__username__icontains=query)
            | Q(user__email__icontains=query)
            | Q(disciplinas__nome__icontains=query)
            | Q(disciplinas__codigo__icontains=query)
        ).distinct()
        professores = professores.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(user__username__icontains=query)
            | Q(user__email__icontains=query)
            | Q(matricula__icontains=query)
            | Q(curso__icontains=query)
            | Q(disciplinas__nome__icontains=query)
            | Q(disciplinas__codigo__icontains=query)
        ).distinct()
        gestores = gestores.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(user__username__icontains=query)
            | Q(user__email__icontains=query)
        ).distinct()

    total_cursos = (
        Aluno.objects.exclude(curso='')
        .values('curso')
        .distinct()
        .count()
    )

    context = {
        'total_alunos': alunos_base.count(),
        'total_professores': professores_base.count(),
        'total_gestores': gestores_base.count(),
        'total_cursos': total_cursos,
        'alunos': alunos,
        'professores': professores,
        'gestores': gestores,
        'query': query,
        'tipo_ativo': tipo_ativo,
        'mostrar_alunos': tipo_ativo in ('todos', 'alunos'),
        'mostrar_professores': tipo_ativo in ('todos', 'professores'),
        'mostrar_gestores': tipo_ativo in ('todos', 'gestao'),
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
        user = form.save()
        request.session.pop('senha_inicial_cadastro_usuario', None)

        role = form.cleaned_data['role']
        email_sender_by_role = {
            Profile.ROLE_ALUNO: enviar_credenciais_acesso_aluno,
            Profile.ROLE_PROFESSOR: enviar_credenciais_acesso_professor,
        }
        email_sender = email_sender_by_role.get(role)

        if email_sender:
            destinatario = None
            if role == Profile.ROLE_PROFESSOR:
                destinatario = form.cleaned_data.get('email_pessoal_professor')

            try:
                email_sender(
                    user,
                    senha_inicial,
                    request,
                    destinatario=destinatario,
                )
            except ImproperlyConfigured as exc:
                logger.warning(
                    'SMTP nao configurado para enviar credenciais do usuario %s.',
                    user.username,
                )
                messages.warning(request, str(exc))
            except SMTPAuthenticationError:
                logger.exception(
                    'Gmail recusou as credenciais SMTP ao enviar acesso do usuario %s.',
                    user.username,
                )
                messages.warning(
                    request,
                    'Usuário cadastrado, mas o Gmail recusou o login SMTP. Use uma senha de app no arquivo .env.',
                )
            except Exception:
                logger.exception(
                    'Falha ao enviar credenciais do usuário %s por e-mail.',
                    user.username,
                )
                messages.warning(
                    request,
                    'Usuário cadastrado, mas não foi possível enviar o e-mail de acesso.',
                )
            else:
                messages.success(
                    request,
                    'Usuário cadastrado com sucesso. Credenciais enviadas para o e-mail do usuário.',
                )
        else:
            messages.success(request, 'Usuário cadastrado com sucesso.')

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
        messages.success(request, 'Aluno atualizado com sucesso.')
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
            'tipo_usuario_form': Profile.ROLE_ALUNO,
        }
    )


@manage_screen_required(Profile.SCREEN_GESTAO)
def editar_professor_gestao(request, id):
    professor = get_object_or_404(
        Profile.objects.select_related('user').prefetch_related('disciplinas'),
        id=id,
        role=Profile.ROLE_PROFESSOR,
    )
    form = GestaoProfessorForm(request.POST or None, instance=professor)

    if form.is_valid():
        form.save()
        messages.success(request, 'Professor atualizado com sucesso.')
        return redirect('dashboard_gestao')

    return render(
        request,
        'gestao/editar_professor.html',
        {
            'professor': professor,
            'form': form,
            'disciplinas_por_curso': disciplinas_por_curso_json(),
        }
    )


@manage_screen_required(Profile.SCREEN_GESTAO)
def excluir_professor_gestao(request, id):
    professor = get_object_or_404(
        Profile.objects.select_related('user'),
        id=id,
        role=Profile.ROLE_PROFESSOR,
    )

    if request.method == 'POST':
        professor.user.delete()
        messages.success(request, 'Professor excluído com sucesso.')
        return redirect('dashboard_gestao')

    return render(
        request,
        'gestao/confirmar_exclusao_professor.html',
        {'professor': professor},
    )


@manage_screen_required(Profile.SCREEN_GESTAO)
def editar_gestor_gestao(request, id):
    gestor = get_object_or_404(
        Profile.objects.select_related('user'),
        id=id,
        role=Profile.ROLE_GESTAO,
    )
    form = GestaoGestorForm(request.POST or None, instance=gestor)

    if form.is_valid():
        form.save()
        messages.success(request, 'Usuário gestão atualizado com sucesso.')
        return redirect('dashboard_gestao')

    return render(
        request,
        'gestao/editar_gestor.html',
        {
            'gestor': gestor,
            'form': form,
        }
    )


@manage_screen_required(Profile.SCREEN_GESTAO)
def excluir_gestor_gestao(request, id):
    gestor = get_object_or_404(
        Profile.objects.select_related('user'),
        id=id,
        role=Profile.ROLE_GESTAO,
    )

    if gestor.user_id == request.user.id:
        messages.error(request, 'Você não pode excluir o próprio usuário gestão.')
        return redirect('dashboard_gestao')

    outros_gestores = Profile.objects.filter(
        role=Profile.ROLE_GESTAO,
    ).exclude(id=gestor.id)
    if not outros_gestores.exists():
        messages.error(request, 'Não é possível excluir o último usuário gestão.')
        return redirect('dashboard_gestao')

    if request.method == 'POST':
        gestor.user.delete()
        messages.success(request, 'Usuário gestão excluído com sucesso.')
        return redirect('dashboard_gestao')

    return render(
        request,
        'gestao/confirmar_exclusao_gestor.html',
        {'gestor': gestor},
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
        messages.success(request, 'Aluno excluído com sucesso.')
        return redirect('dashboard_gestao')

    return render(
        request,
        'gestao/confirmar_exclusao.html',
        {'aluno': aluno}
    )
