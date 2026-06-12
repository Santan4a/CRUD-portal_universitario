from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from alunos.models import Aluno
from disciplinas.models import Disciplina
from users.models import Profile
from .forms import NotaForm
from .models import Nota


@override_settings(SECURE_SSL_REDIRECT=False)
class NotaDeleteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='professor_notas_teste',
            password='admin12345'
        )
        self.profile = Profile.objects.create(user=self.user, role='professor')
        self.client.force_login(self.user)
        self.aluno = Aluno.objects.create(nome='Ana Silva', matricula='N101')
        self.disciplina = Disciplina.objects.create(nome='Matematica', codigo='MAT101')
        self.profile.disciplinas.add(self.disciplina)
        self.aluno.disciplinas.add(self.disciplina)
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
        aluno.disciplinas.add(disciplina)
        Nota.objects.create(aluno=aluno, disciplina=disciplina, nota1=8, nota2=7)
        Nota.objects.create(aluno=outro_aluno, disciplina=disciplina, nota1=4, nota2=5)
        self.client.force_login(aluno_user)

        response = self.client.get(reverse('lista_notas'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ana Silva')
        self.assertContains(response, reverse('exportar_notas_aluno'))
        self.assertContains(response, 'Exportar Notas')
        self.assertNotContains(response, 'Bruno Lima')

    def test_student_cannot_create_nota(self):
        aluno_user = User.objects.create_user(username='aluno_sem_permissao_notas', password='aluno12345')
        Profile.objects.create(user=aluno_user, role='aluno')
        self.client.force_login(aluno_user)

        response = self.client.get(reverse('criar_nota'))

        self.assertEqual(response.status_code, 403)

    def test_gestao_can_create_nota(self):
        gestao_user = User.objects.create_user(
            username='gestao_cria_nota',
            password='gestao12345'
        )
        Profile.objects.create(user=gestao_user, role='gestao')
        aluno = Aluno.objects.create(nome='Ana Silva', matricula='N104')
        disciplina = Disciplina.objects.create(nome='Matematica', codigo='MAT103')
        aluno.disciplinas.add(disciplina)
        self.client.force_login(gestao_user)

        response = self.client.post(
            reverse('criar_nota'),
            {
                'aluno': aluno.id,
                'disciplina': disciplina.id,
                'nota1': 9,
                'nota2': 8,
            },
        )

        self.assertRedirects(response, reverse('lista_notas'))
        self.assertTrue(Nota.objects.filter(
            aluno=aluno,
            disciplina=disciplina,
            nota1=9,
            nota2=8,
        ).exists())

    def test_gestao_can_edit_nota(self):
        gestao_user = User.objects.create_user(
            username='gestao_edita_nota',
            password='gestao12345'
        )
        Profile.objects.create(user=gestao_user, role='gestao')
        aluno = Aluno.objects.create(nome='Ana Silva', matricula='N105')
        disciplina = Disciplina.objects.create(nome='Matematica', codigo='MAT104')
        aluno.disciplinas.add(disciplina)
        nota = Nota.objects.create(
            aluno=aluno,
            disciplina=disciplina,
            nota1=6,
            nota2=7,
        )
        self.client.force_login(gestao_user)

        response = self.client.post(
            reverse('editar_nota', args=[nota.id]),
            {
                'aluno': aluno.id,
                'disciplina': disciplina.id,
                'nota1': 8,
                'nota2': 9,
            },
        )

        nota.refresh_from_db()
        self.assertRedirects(response, reverse('lista_notas'))
        self.assertEqual(nota.nota1, 8)
        self.assertEqual(nota.nota2, 9)

    def test_gestao_lista_notas_with_delete_action(self):
        gestao_user = User.objects.create_user(
            username='gestao_lista_nota',
            password='gestao12345'
        )
        Profile.objects.create(user=gestao_user, role='gestao')
        aluno = Aluno.objects.create(nome='Ana Silva', matricula='N106')
        disciplina = Disciplina.objects.create(nome='Matematica', codigo='MAT105')
        Nota.objects.create(aluno=aluno, disciplina=disciplina, nota1=8, nota2=7)
        self.client.force_login(gestao_user)

        response = self.client.get(reverse('lista_notas'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nova Nota')
        self.assertContains(response, 'Editar')
        self.assertContains(response, 'Excluir')

    def test_gestao_can_delete_nota(self):
        gestao_user = User.objects.create_user(
            username='gestao_nao_deleta_nota',
            password='gestao12345'
        )
        Profile.objects.create(user=gestao_user, role='gestao')
        aluno = Aluno.objects.create(nome='Ana Silva', matricula='N107')
        disciplina = Disciplina.objects.create(nome='Matematica', codigo='MAT106')
        nota = Nota.objects.create(
            aluno=aluno,
            disciplina=disciplina,
            nota1=8,
            nota2=7,
        )
        self.client.force_login(gestao_user)

        response = self.client.post(reverse('deletar_nota', args=[nota.id]))

        self.assertRedirects(response, reverse('lista_notas'))
        self.assertFalse(Nota.objects.filter(id=nota.id).exists())

    def test_nota_form_starts_without_all_disciplines(self):
        form = NotaForm()

        self.assertFalse(form.fields['disciplina'].queryset.exists())

    def test_nota_form_filters_disciplines_by_selected_student(self):
        aluno = Aluno.objects.create(nome='Ana Silva', matricula='N108')
        disciplina_do_aluno = Disciplina.objects.create(
            nome='Matematica',
            codigo='MAT107'
        )
        outra_disciplina = Disciplina.objects.create(
            nome='Fisica',
            codigo='FIS101'
        )
        aluno.disciplinas.add(disciplina_do_aluno)

        form = NotaForm(data={'aluno': aluno.id})

        self.assertIn(disciplina_do_aluno, form.fields['disciplina'].queryset)
        self.assertNotIn(outra_disciplina, form.fields['disciplina'].queryset)

    def test_professor_only_sees_notes_from_own_disciplines(self):
        professor = User.objects.create_user(
            username='professor_escopo_notas',
            password='prof12345',
        )
        profile = Profile.objects.create(user=professor, role='professor')
        disciplina_professor = Disciplina.objects.create(
            nome='Banco de Dados',
            codigo='BD101',
        )
        outra_disciplina = Disciplina.objects.create(
            nome='Redes',
            codigo='RED101',
        )
        profile.disciplinas.add(disciplina_professor)
        aluno_visivel = Aluno.objects.create(nome='Aluno Visivel', matricula='N200')
        aluno_oculto = Aluno.objects.create(nome='Aluno Oculto', matricula='N201')
        aluno_visivel.disciplinas.add(disciplina_professor)
        aluno_oculto.disciplinas.add(outra_disciplina)
        Nota.objects.create(
            aluno=aluno_visivel,
            disciplina=disciplina_professor,
            nota1=8,
            nota2=9,
        )
        Nota.objects.create(
            aluno=aluno_oculto,
            disciplina=outra_disciplina,
            nota1=5,
            nota2=6,
        )
        self.client.force_login(professor)

        response = self.client.get(reverse('lista_notas'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aluno Visivel')
        self.assertNotContains(response, 'Aluno Oculto')

    def test_nota_form_rejects_discipline_outside_student_course(self):
        aluno = Aluno.objects.create(nome='Ana Silva', matricula='N109')
        disciplina_do_aluno = Disciplina.objects.create(
            nome='Matematica',
            codigo='MAT108'
        )
        outra_disciplina = Disciplina.objects.create(
            nome='Fisica',
            codigo='FIS102'
        )
        aluno.disciplinas.add(disciplina_do_aluno)

        form = NotaForm(data={
            'aluno': aluno.id,
            'disciplina': outra_disciplina.id,
            'nota1': 8,
            'nota2': 7,
        })

        self.assertFalse(form.is_valid())
        self.assertIn('disciplina', form.errors)

