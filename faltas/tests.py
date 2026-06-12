from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from alunos.models import Aluno
from disciplinas.models import Disciplina
from users.models import Profile
from .models import Chamada, Falta, PresencaChamada


@override_settings(SECURE_SSL_REDIRECT=False)
class FaltaAccessTests(TestCase):
    def setUp(self):
        self.disciplina = Disciplina.objects.create(nome='Matematica', codigo='FAL101')

    def test_professor_can_create_falta(self):
        professor = User.objects.create_user(username='professor_faltas_teste', password='professor12345')
        profile = Profile.objects.create(user=professor, role='professor')
        profile.disciplinas.add(self.disciplina)
        aluno = Aluno.objects.create(nome='Ana Silva', matricula='F101')
        aluno.disciplinas.add(self.disciplina)
        self.client.force_login(professor)

        response = self.client.post(
            reverse('criar_falta'),
            {
                'aluno': aluno.id,
                'disciplina': self.disciplina.id,
                'data': '2026-05-13',
                'justificada': '',
            }
        )

        self.assertRedirects(response, reverse('lista_faltas'))
        self.assertTrue(Falta.objects.filter(aluno=aluno).exists())

    def test_student_only_sees_own_faltas(self):
        aluno_user = User.objects.create_user(username='aluno_faltas_teste', password='aluno12345')
        Profile.objects.create(user=aluno_user, role='aluno')
        aluno = Aluno.objects.create(user=aluno_user, nome='Ana Silva', matricula='F102')
        aluno.disciplinas.add(self.disciplina)
        outro_aluno = Aluno.objects.create(nome='Bruno Lima', matricula='F103')
        Falta.objects.create(aluno=aluno, disciplina=self.disciplina, data=date(2026, 5, 13))
        Falta.objects.create(aluno=outro_aluno, disciplina=self.disciplina, data=date(2026, 5, 12))
        self.client.force_login(aluno_user)

        response = self.client.get(reverse('lista_faltas'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ana Silva')
        self.assertNotContains(response, 'Bruno Lima')

    def test_gestao_nao_ve_nem_acessa_registrar_chamada(self):
        gestao = User.objects.create_user(username='gestao_faltas_teste', password='gestao12345')
        Profile.objects.create(user=gestao, role='gestao')
        self.client.force_login(gestao)

        lista_response = self.client.get(reverse('lista_faltas'))
        chamada_response = self.client.get(reverse('registrar_chamada'))

        self.assertEqual(lista_response.status_code, 200)
        self.assertContains(lista_response, 'Nova Falta')
        self.assertContains(lista_response, 'Limites')
        self.assertNotContains(lista_response, 'Registrar chamada')
        self.assertEqual(chamada_response.status_code, 403)

    def test_professor_ve_registrar_chamada(self):
        professor = User.objects.create_user(username='professor_botao_chamada', password='professor12345')
        profile = Profile.objects.create(user=professor, role='professor')
        profile.disciplinas.add(self.disciplina)
        self.client.force_login(professor)

        response = self.client.get(reverse('lista_faltas'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Registrar chamada')

    def test_professor_registra_chamada_e_gera_faltas(self):
        professor = User.objects.create_user(
            username='professor_chamada',
            password='professor12345',
        )
        profile = Profile.objects.create(user=professor, role='professor')
        profile.disciplinas.add(self.disciplina)
        aluno_presente = Aluno.objects.create(nome='Aluno Presente', matricula='F201')
        aluno_faltou = Aluno.objects.create(nome='Aluno Faltou', matricula='F202')
        aluno_presente.disciplinas.add(self.disciplina)
        aluno_faltou.disciplinas.add(self.disciplina)
        self.client.force_login(professor)

        response = self.client.post(
            reverse('registrar_chamada'),
            {
                'disciplina': self.disciplina.id,
                'data': '2026-05-14',
                'presentes': [str(aluno_presente.id)],
            },
        )

        self.assertRedirects(response, reverse('lista_faltas'))
        chamada = Chamada.objects.get(disciplina=self.disciplina)
        self.assertEqual(chamada.presencas.count(), 2)
        self.assertTrue(PresencaChamada.objects.get(
            chamada=chamada,
            aluno=aluno_presente,
        ).presente)
        self.assertTrue(Falta.objects.filter(
            aluno=aluno_faltou,
            disciplina=self.disciplina,
            data='2026-05-14',
        ).exists())

