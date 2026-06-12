from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.urls import reverse


def validar_backend_email_real():
    if settings.EMAIL_BACKEND.endswith('console.EmailBackend'):
        raise ImproperlyConfigured(
            'SMTP de e-mail nao configurado. Crie o arquivo .env com '
            'DJANGO_EMAIL_HOST, DJANGO_EMAIL_HOST_USER e '
            'DJANGO_EMAIL_HOST_PASSWORD para enviar as credenciais por e-mail.'
        )


def enviar_credenciais_acesso_usuario(
    user,
    senha_inicial,
    request=None,
    incluir_email_institucional=False,
    destinatario=None,
    dados_adicionais='',
):
    validar_backend_email_real()

    login_path = reverse('login')
    login_url = request.build_absolute_uri(login_path) if request else login_path
    nome = user.get_full_name() or user.first_name or user.username
    linha_email = (
        f'E-mail institucional: {user.email}' + chr(10)
        if incluir_email_institucional else ''
    )
    dados_adicionais = dados_adicionais.strip()
    bloco_dados_adicionais = (
        chr(10) + chr(10) + dados_adicionais
        if dados_adicionais else ''
    )

    assunto = 'Seu acesso ao Portal Universitario'
    mensagem = f"""Ola, {nome}!

Seu cadastro no Portal Universitario foi realizado.

Usuario: {user.username}
{linha_email}Senha inicial: {senha_inicial}
{bloco_dados_adicionais}

Acesse o portal em: {login_url}

Por seguranca, nao compartilhe estes dados de acesso."""

    return send_mail(
        assunto,
        mensagem,
        settings.DEFAULT_FROM_EMAIL,
        [destinatario or user.email],
        fail_silently=False,
    )


def enviar_credenciais_acesso_aluno(
    user,
    senha_inicial,
    request=None,
    destinatario=None,
):
    aluno = getattr(user, 'aluno', None)
    dados_aluno = ''

    if aluno:
        disciplinas = aluno.disciplinas.order_by('nome', 'codigo')
        disciplinas_texto = ', '.join(
            f'{disciplina.nome} ({disciplina.codigo})'
            for disciplina in disciplinas
        ) or 'Nenhuma disciplina vinculada'
        turno = aluno.get_turno_display() if aluno.turno else 'Nao informado'

        dados_aluno = f"""Dados do aluno:
Nome: {aluno.nome}
Matricula: {aluno.matricula}
Curso: {aluno.curso or 'Nao informado'}
Turno: {turno}
Disciplinas: {disciplinas_texto}"""

    return enviar_credenciais_acesso_usuario(
        user,
        senha_inicial,
        request,
        destinatario=destinatario,
        dados_adicionais=dados_aluno,
    )


def enviar_credenciais_acesso_professor(
    user,
    senha_inicial,
    request=None,
    destinatario=None,
):
    return enviar_credenciais_acesso_usuario(
        user,
        senha_inicial,
        request,
        incluir_email_institucional=True,
        destinatario=destinatario,
    )
