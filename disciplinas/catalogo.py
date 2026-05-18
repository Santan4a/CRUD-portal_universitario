import json
from functools import lru_cache
from pathlib import Path

from .models import Disciplina


CATALOGO_PATH = Path(__file__).resolve().parent / 'data' / 'cursos_disciplinas.json'


@lru_cache
def carregar_matriz_curricular():
    with CATALOGO_PATH.open(encoding='utf-8') as arquivo:
        return json.load(arquivo)


def cursos_disponiveis():
    return list(carregar_matriz_curricular().keys())


def curso_choices():
    choices = [('', 'Selecione um curso')]
    choices.extend((curso, curso) for curso in cursos_disponiveis())
    return choices


def disciplinas_do_curso(curso):
    if not curso:
        return []
    return carregar_matriz_curricular().get(curso, [])


def disciplinas_por_curso_json():
    return {
        curso: list(disciplinas)
        for curso, disciplinas in carregar_matriz_curricular().items()
    }


def obter_ou_criar_disciplinas_do_curso(curso):
    disciplinas = []

    for item in disciplinas_do_curso(curso):
        disciplina, _ = Disciplina.objects.get_or_create(
            codigo=item['codigo'],
            defaults={'nome': item['nome']},
        )

        if disciplina.nome != item['nome']:
            disciplina.nome = item['nome']
            disciplina.save(update_fields=['nome'])

        disciplinas.append(disciplina)

    return disciplinas


def vincular_disciplinas_do_curso(aluno):
    disciplinas = obter_ou_criar_disciplinas_do_curso(aluno.curso)
    aluno.disciplinas.set(disciplinas)
    return disciplinas
