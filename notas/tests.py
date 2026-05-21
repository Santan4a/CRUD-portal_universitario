from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from alunos.models import Aluno
from disciplinas.models import Disciplina
from users.models import Profile
from .models import Nota


@override_settings(SECURE_SSL_REDIRECT=False)
class NotaDeleteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='professor_notas_teste',
            password='admin12345'
        )
        Profile.objects.create(user=self.user, role='professor')
        self.client.force_login(self.user)
        self.aluno = Aluno.objects.create(nome='Ana Silva', matricula='N101')
        self.disciplina = Disciplina.objects.create(nome='Matematica', codigo='MAT101')
        self.nota = Nota.objects.create(
            aluno=self.aluno,
            disciplina=self.disciplina,
            nota1=8,
            nota2=7,
        )

    def test_get_delete_page_does_not_delete_nota(self):
        response = self.client.get(reverse('deletar_nota', args=[self.nota.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notas/confirmar_exclusao.html')
        self.assertTrue(Nota.objects.filter(id=self.nota.id).exists())

    def test_post_delete_removes_nota(self):
        response = self.client.post(reverse('deletar_nota', args=[self.nota.id]))

        self.assertRedirects(response, reverse('lista_notas'))
        self.assertFalse(Nota.objects.filter(id=self.nota.id).exists())


@override_settings(SECURE_SSL_REDIRECT=False)
class NotaAccessTests(TestCase):
    def test_student_only_sees_own_notas(self):
        aluno_user = User.objects.create_user(username='aluno_notas_teste', password='aluno12345')
        Profile.objects.create(user=aluno_user, role='aluno')
        aluno = Aluno.objects.create(
            user=aluno_user,
            nome='Ana Silva',
            matricula='N102',
            curso='Bacharelado em Sistemas de Informação e Transformação Digital'
        )
        outro_aluno = Aluno.objects.create(nome='Bruno Lima', matricula='N103')
        disciplina = Disciplina.objects.create(nome='Matematica', codigo='MAT102')
        Nota.objects.create(aluno=aluno, disciplina=disciplina, nota1=8, nota2=7)
        Nota.objects.create(aluno=outro_aluno, disciplina=disciplina, nota1=4, nota2=5)
        self.client.force_login(aluno_user)

        response = self.client.get(reverse('lista_notas'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ana Silva')
        self.assertNotContains(response, 'Bruno Lima')

    def test_student_cannot_create_nota(self):
        aluno_user = User.objects.create_user(username='aluno_sem_permissao_notas', password='aluno12345')
        Profile.objects.create(user=aluno_user, role='aluno')
        self.client.force_login(aluno_user)

        response = self.client.get(reverse('criar_nota'))

        self.assertEqual(response.status_code, 403)
