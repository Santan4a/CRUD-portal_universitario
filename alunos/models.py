from django.db import models
from django.conf import settings

from users.utils import gerar_matricula_unica


class Aluno(models.Model):
    TURNO_MANHA = 'manha'
    TURNO_TARDE = 'tarde'
    TURNO_NOITE = 'noite'

    TURNO_CHOICES = (
        (TURNO_MANHA, 'Manhã'),
        (TURNO_TARDE, 'Tarde'),
        (TURNO_NOITE, 'Noite'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='aluno',
        verbose_name='usuario de acesso'
    )
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20, unique=True, blank=True)
    curso = models.CharField(max_length=120, blank=True, default='')
    turno = models.CharField(
        max_length=10,
        choices=TURNO_CHOICES,
        blank=True,
        default='',
    )
    disciplinas = models.ManyToManyField(
        'disciplinas.Disciplina',
        blank=True,
        related_name='alunos'
    )

    @classmethod
    def gerar_matricula(cls):
        return gerar_matricula_unica('aluno', cls)

    def save(self, *args, **kwargs):
        if not self.matricula:
            self.matricula = self.__class__.gerar_matricula()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.matricula}"
