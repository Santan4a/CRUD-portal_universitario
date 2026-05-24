import re
import secrets
from django.utils import timezone


PREFIXOS_MATRICULA = {
    'aluno': 'ALU',
    'professor': 'PROF',
    'gestao': 'GEST',
}

DOMINIO_EMAIL_INSTITUCIONAL = 'portaltech.com'
CARACTERES_SENHA_INICIAL = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789'


def obter_prefixo_matricula(role):
    role_normalizada = (role or '').strip().lower()

    if role_normalizada not in PREFIXOS_MATRICULA:
        raise ValueError(f'Role invalida para geracao de matricula: {role}')

    return PREFIXOS_MATRICULA[role_normalizada]


def gerar_codigo_sequencial_unico(prefixo, modelos_campos):
    ano = timezone.localdate().year
    base = f'{prefixo}{ano}'
    padrao = re.compile(rf'^{base}(\d{{4}})$')
    maior_sequencia = 0

    for model, campo in modelos_campos:
        filtro_inicio = {f'{campo}__startswith': base}
        valores = model.objects.filter(**filtro_inicio).values_list(campo, flat=True)

        for valor in valores:
            resultado = padrao.match(valor or '')
            if resultado:
                maior_sequencia = max(maior_sequencia, int(resultado.group(1)))

    proxima_sequencia = maior_sequencia + 1

    while True:
        novo_codigo = f'{base}{proxima_sequencia:04d}'
        codigo_existe = False

        for model, campo in modelos_campos:
            filtro_exato = {campo: novo_codigo}
            if model.objects.filter(**filtro_exato).exists():
                codigo_existe = True
                break

        if not codigo_existe:
            return novo_codigo

        proxima_sequencia += 1


def gerar_matricula_unica(role, profile_model):
    prefixo = obter_prefixo_matricula(role)

    return gerar_codigo_sequencial_unico(prefixo, [(profile_model, 'matricula')])


def gerar_usuario_aluno_unico(user_model, profile_model, aluno_model):
    prefixo = obter_prefixo_matricula('aluno')

    return gerar_codigo_sequencial_unico(
        prefixo,
        [
            (user_model, 'username'),
            (profile_model, 'matricula'),
            (aluno_model, 'matricula'),
        ]
    )


def gerar_usuario_professor_unico(user_model, profile_model):
    prefixo = obter_prefixo_matricula('professor')

    return gerar_codigo_sequencial_unico(
        prefixo,
        [
            (user_model, 'username'),
            (profile_model, 'matricula'),
        ]
    )


def gerar_email_institucional(username):
    usuario = (username or '').strip().lower()

    if not usuario:
        return ''

    return f'{usuario}@{DOMINIO_EMAIL_INSTITUCIONAL}'


def gerar_senha_inicial_aleatoria(tamanho=10):
    return ''.join(
        secrets.choice(CARACTERES_SENHA_INICIAL)
        for _ in range(tamanho)
    )
