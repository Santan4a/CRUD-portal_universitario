from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def enviar_credenciais_acesso_usuario(
    user,
    senha_inicial,
    request=None,
    incluir_email_institucional=False,
    destinatario=None,
):
    login_path = reverse('login')
    login_url = request.build_absolute_uri(login_path) if request else login_path
    nome = user.get_full_name() or user.first_name or user.username
    linha_email = (
        f'E-mail institucional: {user.email}' + chr(10)
        if incluir_email_institucional else ''
    )

    assunto = 'Seu acesso ao Portal Universitario'
    mensagem = f"""Ola, {nome}!

Seu cadastro no Portal Universitario foi realizado.

Usuario: {user.username}
{linha_email}Senha inicial: {senha_inicial}

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
    return enviar_credenciais_acesso_usuario(
        user,
        senha_inicial,
        request,
        destinatario=destinatario,
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
