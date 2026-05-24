from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    ROLE_ALUNO = 'aluno'
    ROLE_PROFESSOR = 'professor'
    ROLE_GESTAO = 'gestao'

    ROLE_CHOICES = (
        (ROLE_ALUNO, 'Aluno'),
        (ROLE_PROFESSOR, 'Professor'),
        (ROLE_GESTAO, 'Gestao'),
    )

    SCREEN_GESTAO = 'gestao'
    SCREEN_ALUNOS = 'alunos'
    SCREEN_DISCIPLINAS = 'disciplinas'
    SCREEN_NOTAS = 'notas'
    SCREEN_FALTAS = 'faltas'

    SCREEN_CHOICES = (
        (SCREEN_GESTAO, 'Gestão'),
        (SCREEN_ALUNOS, 'Alunos'),
        (SCREEN_DISCIPLINAS, 'Disciplinas'),
        (SCREEN_NOTAS, 'Notas'),
        (SCREEN_FALTAS, 'Faltas'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    allowed_screens = models.JSONField(
        blank=True,
        default=None,
        null=True,
        verbose_name='telas permitidas',
    )
    curso = models.CharField(max_length=120, blank=True, default='')
    disciplinas = models.ManyToManyField(
        'disciplinas.Disciplina',
        blank=True,
        related_name='professores',
        verbose_name='disciplinas lecionadas',
    )

    matricula = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
        editable=False,
    )

    def __str__(self):
        return f'{self.user.username} - {self.matricula or "sem matricula"}'