from datetime import time

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from alunos.models import Aluno
from cronograma.models import Cronograma
from disciplinas.models import Disciplina
from users.models import Profile


@override_settings(SECURE_SSL_REDIRECT=False)
class CronogramaViewTests(TestCase):
    def test_aluno_ve_apenas_horarios_do_proprio_turno(self):
        disciplina = Disciplina.objects.create(
            nome='Programacao',
            codigo='PROG-TURNO',
        )
        aluno_user = User.objects.create_user(
            username='aluno.cronograma.turno',
            password='aluno12345',
        )
        Profile.objects.create(user=aluno_user, role=Profile.ROLE_ALUNO)
        aluno = Aluno.objects.create(
            user=aluno_user,
            nome='Aluno Cronograma',
            matricula='ALUTURNO001',
            turno=Aluno.TURNO_TARDE,
        )
        aluno.disciplinas.add(disciplina)
        Cronograma.objects.create(
            disciplina=disciplina,
            dia_semana='TER',
            turno=Cronograma.TURNO_MANHA,
            horario_inicio=time(7, 30),
            horario_fim=time(9, 10),
            sala='MANHA-01',
        )
        Cronograma.objects.create(
            disciplina=disciplina,
            dia_semana='TER',
            turno=Cronograma.TURNO_TARDE,
            horario_inicio=time(13, 30),
            horario_fim=time(15, 10),
            sala='TARDE-01',
        )
        self.client.force_login(aluno_user)

        response = self.client.get(reverse('grade_horarios'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tarde')
        self.assertContains(response, '13:30')
        self.assertNotContains(response, 'Manhã')
        self.assertNotContains(response, '07:30')
