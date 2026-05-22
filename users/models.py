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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

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