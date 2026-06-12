from django.db import models
from disciplinas.models import Disciplina

class Cronograma(models.Model):
    TURNO_MANHA = 'manha'
    TURNO_TARDE = 'tarde'
    TURNO_NOITE = 'noite'

    TURNO_CHOICES = (
        (TURNO_MANHA, 'Manhã'),
        (TURNO_TARDE, 'Tarde'),
        (TURNO_NOITE, 'Noite'),
    )

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

    turno = models.CharField(
        max_length=10,
        choices=TURNO_CHOICES,
        default=TURNO_NOITE,
    )

    horario_inicio = models.TimeField()

    horario_fim = models.TimeField()

    sala = models.CharField(
        max_length=50
    )

    def __str__(self):
        return f'{self.disciplina.nome} - {self.get_turno_display()} - {self.dia_semana}'