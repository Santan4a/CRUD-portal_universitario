import random

from datetime import time

from django.core.management.base import BaseCommand

from cronograma.models import Cronograma
from disciplinas.models import Disciplina


DIAS = [
    'SEG',
    'TER',
    'QUA',
    'QUI',
    'SEX',
]

BLOCOS_POR_TURNO = {
    Cronograma.TURNO_MANHA: [
        (time(7, 30), time(9, 10)),
        (time(9, 10), time(10, 50)),
        (time(10, 50), time(12, 30)),
    ],
    Cronograma.TURNO_TARDE: [
        (time(13, 30), time(15, 10)),
        (time(15, 10), time(16, 50)),
        (time(16, 50), time(18, 30)),
    ],
    Cronograma.TURNO_NOITE: [
        (time(18, 50), time(20, 30)),
        (time(20, 30), time(22, 10)),
        (time(22, 10), time(23, 0)),
    ],
}

SALAS = [
    'LAB-01',
    'LAB-02',
    'SALA-101',
    'SALA-202',
]


class Command(BaseCommand):
    help = 'Gera cronogramas humanizados automaticamente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove os cronogramas existentes antes de gerar novos.',
        )

    def handle(self, *args, **kwargs):
        if kwargs.get('reset'):
            removidos, _ = Cronograma.objects.all().delete()
            self.stdout.write(f'{removidos} registro(s) de cronograma removido(s).')

        disciplinas = Disciplina.objects.order_by('codigo', 'nome')
        criados = 0
        mantidos = 0

        for disciplina in disciplinas:
            for turno, blocos in BLOCOS_POR_TURNO.items():
                existentes = Cronograma.objects.filter(
                    disciplina=disciplina,
                    turno=turno,
                )
                if existentes.exists():
                    mantidos += existentes.count()
                    continue

                random.seed(f'{disciplina.codigo}:{turno}')
                quantidade_dias = min(2, len(DIAS))
                dias_escolhidos = random.sample(DIAS, quantidade_dias)

                for indice, dia in enumerate(dias_escolhidos):
                    bloco = blocos[indice % len(blocos)]
                    Cronograma.objects.create(
                        disciplina=disciplina,
                        dia_semana=dia,
                        turno=turno,
                        horario_inicio=bloco[0],
                        horario_fim=bloco[1],
                        sala=random.choice(SALAS),
                    )
                    criados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Cronograma pronto: {criados} aula(s) criada(s), {mantidos} aula(s) mantida(s).'
            )
        )
