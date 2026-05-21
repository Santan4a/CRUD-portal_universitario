from django.db import models
from django.conf import settings


class Aluno(models.Model):
    MATRICULA_PREFIXO = 'A'
    MATRICULA_DIGITOS = 3

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='aluno',
        verbose_name='usuario de acesso'
    )
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=10, unique=True, blank=True)
    curso = models.CharField(max_length=120, blank=True, default='')
    disciplinas = models.ManyToManyField(
        'disciplinas.Disciplina',
        blank=True,
        related_name='alunos'
    )

    @classmethod
    def gerar_matricula(cls):
        maior_numero = 0
        matriculas = cls.objects.filter(
            matricula__startswith=cls.MATRICULA_PREFIXO
        ).values_list('matricula', flat=True)

        for matricula in matriculas:
            numero = matricula[len(cls.MATRICULA_PREFIXO):]
            if numero.isdigit():
                maior_numero = max(maior_numero, int(numero))

        proximo_numero = maior_numero + 1
        while True:
            matricula = (
                f"{cls.MATRICULA_PREFIXO}"
                f"{proximo_numero:0{cls.MATRICULA_DIGITOS}d}"
            )
            if not cls.objects.filter(matricula=matricula).exists():
                return matricula
            proximo_numero += 1

    def save(self, *args, **kwargs):
        if not self.matricula:
            self.matricula = self.__class__.gerar_matricula()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.matricula}"
