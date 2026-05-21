import re
from django.utils import timezone


PREFIXOS_MATRICULA = {
    'aluno': 'ALU',
    'professor': 'PROF',
    'gestao': 'GEST',
}


def obter_prefixo_matricula(role):
    role_normalizada = (role or '').strip().lower()

    if role_normalizada not in PREFIXOS_MATRICULA:
        raise ValueError(f'Role invalida para geracao de matricula: {role}')

    return PREFIXOS_MATRICULA[role_normalizada]


def gerar_matricula_unica(role, profile_model):
    prefixo = obter_prefixo_matricula(role)
    ano = timezone.localdate().year
    base = f'{prefixo}{ano}'

    padrao = re.compile(rf'^{base}(\d{{4}})$')

    matriculas = profile_model.objects.filter(
        matricula__startswith=base
    ).values_list('matricula', flat=True)

    maior_sequencia = 0

    for matricula in matriculas:
        resultado = padrao.match(matricula or '')
        if resultado:
            maior_sequencia = max(maior_sequencia, int(resultado.group(1)))

    proxima_sequencia = maior_sequencia + 1

    while True:
        nova_matricula = f'{base}{proxima_sequencia:04d}'

        if not profile_model.objects.filter(matricula=nova_matricula).exists():
            return nova_matricula

        proxima_sequencia += 1