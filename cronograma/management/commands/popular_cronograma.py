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

BLOCOS = [
    (time(18, 50), time(20, 30)),
    (time(20, 30), time(22, 10)),
    (time(22, 10), time(23, 0)),
]

SALAS = [
    'LAB-01',
    'LAB-02',
    'SALA-101',
    'SALA-202',
]


class Command(BaseCommand):

    help = 'Gera cronogramas humanizados automaticamente'

    def handle(self, *args, **kwargs):

        # limpa cronogramas antigos
        Cronograma.objects.all().delete()

        disciplinas = Disciplina.objects.all()

        for disciplina in disciplinas:

            # quantidade de dias que a disciplina aparece
            quantidade_dias = random.randint(1, 3)

            dias_escolhidos = random.sample(
                DIAS,
                quantidade_dias
            )

            for dia in dias_escolhidos:

                # alguns dias têm mais aulas que outros
                quantidade_blocos = random.randint(1, 3)

                blocos_escolhidos = random.sample(
                    BLOCOS,
                    quantidade_blocos
                )

                for bloco in blocos_escolhidos:

                    Cronograma.objects.create(

                        disciplina=disciplina,

                        dia_semana=dia,

                        horario_inicio=bloco[0],

                        horario_fim=bloco[1],

                        sala=random.choice(SALAS)
                    )

        self.stdout.write(
            self.style.SUCCESS(
                'Cronogramas humanizados criados com sucesso!'
            )
        )