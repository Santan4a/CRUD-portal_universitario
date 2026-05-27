from django.db import models
from disciplinas.models import Disciplina

class Cronograma(models.Model):

    DIAS =  [
        ('SEG', 'Segunda'),
        ('TER', 'Terça'),
        ('QUA', 'Quarta'),
        ('QUI', 'Quinta'),
        ('SEX', 'Sexta'),
    ]

    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE
    )
    
    dia_semana = models.CharField(
        max_length=3,
        choices=DIAS
    )

    horario_inicio = models.TimeField()

    horario_fim = models.TimeField()

    sala = models.CharField(
        max_length=50
    )

    def __str__(self):
        return f'{self.disciplina.nome} - {self.dia_semana}'