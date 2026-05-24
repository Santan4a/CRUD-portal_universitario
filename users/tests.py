from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from alunos.models import Aluno
from disciplinas.catalogo import cursos_disponiveis, disciplinas_do_curso
from disciplinas.models import Disciplina
from users.access import get_default_screens_for_role
from users.utils import gerar_email_institucional, gerar_senha_inicial_aleatoria, gerar_usuario_aluno_unico, gerar_usuario_professor_unico
from users.forms import GestaoUsuarioForm
from users.models import Profile


class GestaoUsuarioFormTests(TestCase):
    def test_salvar_cria_professor_com_telas_padrao(self):
        ano = timezone.localdate().year
        curso = cursos_disponiveis()[0]
        disciplina = disciplinas_do_curso(curso)[0]
        senha_inicial = 'SenhaABC123'
        form = GestaoUsuarioForm(data={
            'role': Profile.ROLE_PROFESSOR,
            'nome': 'Professor Silva',
            'email': 'professor@example.com',
            'password': 'senha-manual',
            'curso': curso,
            'disciplina': disciplina['codigo'],
        }, initial_password=senha_inicial)

        self.assertTrue(form.is_valid(), form.errors)

        user = form.save()
        self.assertEqual(user.first_name, 'Professor Silva')
        self.assertEqual(user.username, f'PROF{ano}0001')
        self.assertEqual(user.email, f'prof{ano}0001@portaltech.com')
        self.assertTrue(user.check_password(senha_inicial))
        self.assertFalse(user.check_password('senha-manual'))
        self.assertEqual(user.profile.role, Profile.ROLE_PROFESSOR)
        self.assertEqual(user.profile.matricula, user.username)
        self.assertEqual(user.profile.curso, curso)
        self.assertEqual(gerar_email_institucional(user.username), user.email)
        self.assertEqual(
            set(user.profile.allowed_screens),
            {Profile.SCREEN_ALUNOS, Profile.SCREEN_NOTAS, Profile.SCREEN_FALTAS},
        )
        self.assertEqual(
            set(user.profile.disciplinas.values_list('codigo', flat=True)),
            {disciplina['codigo']},
        )
        self.assertFalse(Aluno.objects.filter(user=user).exists())

    def test_salvar_cria_aluno_com_usuario_matricula_e_disciplinas(self):
        ano = timezone.localdate().year
        curso = cursos_disponiveis()[0]
        senha_inicial = 'AlunoABC123'
        form = GestaoUsuarioForm(data={
            'role': Profile.ROLE_ALUNO,
            'nome': 'Ana Silva',
            'email': 'ana@example.com',
            'password': 'senha-manual',
            'curso': curso,
        }, initial_password=senha_inicial)

        self.assertTrue(form.is_valid(), form.errors)

        user = form.save()
        aluno = user.aluno
        codigos_esperados = {
            disciplina['codigo']
            for disciplina in disciplinas_do_curso(curso)
        }

        self.assertEqual(user.username, f'ALU{ano}0001')
        self.assertTrue(user.check_password(senha_inicial))
        self.assertFalse(user.check_password('senha-manual'))
        self.assertEqual(user.profile.role, Profile.ROLE_ALUNO)
        self.assertEqual(user.profile.matricula, user.username)
        self.assertEqual(user.profile.curso, curso)
        self.assertEqual(aluno.nome, 'Ana Silva')
        self.assertEqual(aluno.matricula, user.username)
        self.assertEqual(aluno.curso, curso)
        self.assertEqual(
            set(aluno.disciplinas.values_list('codigo', flat=True)),
            codigos_esperados,
        )

    def test_telas_vem_predefinidas_por_tipo_de_usuario(self):
        self.assertEqual(
            set(get_default_screens_for_role(Profile.ROLE_PROFESSOR)),
            {Profile.SCREEN_ALUNOS, Profile.SCREEN_NOTAS, Profile.SCREEN_FALTAS},
        )
        self.assertEqual(
            set(get_default_screens_for_role(Profile.ROLE_GESTAO)),
            {screen for screen, _ in Profile.SCREEN_CHOICES},
        )

    def test_ignora_usuario_e_permissoes_enviados_para_aluno_e_professor(self):
        curso = cursos_disponiveis()[0]
        disciplina = disciplinas_do_curso(curso)[0]
        aluno_form = GestaoUsuarioForm(data={
            'role': Profile.ROLE_ALUNO,
            'nome': 'Ana Silva',
            'username': 'aluno.manual',
            'password': 'aluno12345',
            'curso': curso,
            'allowed_screens': [Profile.SCREEN_GESTAO],
        })
        professor_form = GestaoUsuarioForm(data={
            'role': Profile.ROLE_PROFESSOR,
            'nome': 'Professor Silva',
            'username': 'professor.sem.tela',
            'password': 'prof12345',
            'curso': curso,
            'disciplina': disciplina['codigo'],
            'allowed_screens': [Profile.SCREEN_GESTAO],
        })

        self.assertTrue(aluno_form.is_valid(), aluno_form.errors)
        self.assertTrue(professor_form.is_valid(), professor_form.errors)

        aluno_user = aluno_form.save()
        professor_user = professor_form.save()

        self.assertNotEqual(aluno_user.username, 'aluno.manual')
        self.assertEqual(aluno_user.profile.matricula, aluno_user.username)
        self.assertEqual(aluno_user.aluno.matricula, aluno_user.username)
        self.assertNotEqual(professor_user.username, 'professor.sem.tela')
        self.assertEqual(professor_user.email, gerar_email_institucional(professor_user.username))
        self.assertEqual(professor_user.profile.matricula, professor_user.username)
        self.assertEqual(
            set(professor_user.profile.allowed_screens),
            {Profile.SCREEN_ALUNOS, Profile.SCREEN_NOTAS, Profile.SCREEN_FALTAS},
        )

    def test_professor_precisa_informar_curso(self):
        form = GestaoUsuarioForm(data={
            'role': Profile.ROLE_PROFESSOR,
            'nome': 'Professor Silva',
            'password': 'prof12345',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('curso', form.errors)

    def test_professor_precisa_informar_disciplina(self):
        curso = cursos_disponiveis()[0]
        form = GestaoUsuarioForm(data={
            'role': Profile.ROLE_PROFESSOR,
            'nome': 'Professor Silva',
            'password': 'prof12345',
            'curso': curso,
        })

        self.assertFalse(form.is_valid())
        self.assertIn('disciplina', form.errors)

    def test_gestao_nao_precisa_informar_curso(self):
        form = GestaoUsuarioForm(data={
            'role': Profile.ROLE_GESTAO,
            'nome': 'Gestor Silva',
            'username': 'gestor.silva',
            'email': 'gestor@example.com',
        }, initial_password='SenhaGestao123')

        self.assertTrue(form.is_valid(), form.errors)

        user = form.save()

        self.assertEqual(user.profile.role, Profile.ROLE_GESTAO)
        self.assertEqual(user.profile.curso, '')
        self.assertEqual(user.profile.disciplinas.count(), 0)

    def test_senha_inicial_aleatoria_tem_tamanho_esperado(self):
        senha = gerar_senha_inicial_aleatoria()

        self.assertEqual(len(senha), 10)
        self.assertRegex(senha, r'^[A-Za-z2-9]+$')

    def test_usuario_aluno_e_professor_seguem_proxima_sequencia_disponivel(self):
        ano = timezone.localdate().year
        User.objects.create_user(username=f'ALU{ano}0004', password='aluno12345')
        User.objects.create_user(username=f'PROF{ano}0004', password='prof12345')

        self.assertEqual(
            gerar_usuario_aluno_unico(User, Profile, Aluno),
            f'ALU{ano}0005',
        )
        self.assertEqual(
            gerar_usuario_professor_unico(User, Profile),
            f'PROF{ano}0005',
        )


@override_settings(SECURE_SSL_REDIRECT=False)
class GestaoUsuarioViewTests(TestCase):
    def setUp(self):
        self.gestao_user = User.objects.create_user(
            username='gestao_usuarios',
            password='gestao12345',
        )
        Profile.objects.create(user=self.gestao_user, role=Profile.ROLE_GESTAO)
        self.client.force_login(self.gestao_user)

    def test_cadastro_usuario_exibe_professor_sem_campo_de_permissoes(self):
        response = self.client.get(reverse('cadastrar_usuario_gestao'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Professor')
        self.assertContains(response, response.context['proximo_usuario_aluno'])
        self.assertContains(response, response.context['proximo_usuario_professor'])
        self.assertContains(response, response.context['email_institucional_professor'])
        self.assertContains(response, response.context['senha_inicial_aleatoria'])
        self.assertNotContains(response, 'Telas permitidas')
        self.assertNotContains(response, 'allowed_screens')

    def test_dashboard_exibe_professores_cadastrados(self):
        curso = cursos_disponiveis()[0]
        disciplina_dados = disciplinas_do_curso(curso)[0]
        disciplina = Disciplina.objects.create(**disciplina_dados)
        professor_user = User.objects.create_user(
            username='professor.dashboard',
            password='prof12345',
            first_name='Professor',
            last_name='Dashboard',
            email='professor.dashboard@portaltech.com',
        )
        professor = Profile.objects.create(
            user=professor_user,
            role=Profile.ROLE_PROFESSOR,
            matricula='PROF20260077',
            curso=curso,
        )
        professor.disciplinas.add(disciplina)

        response = self.client.get(reverse('dashboard_gestao'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Professores cadastrados')
        self.assertContains(response, 'Professor Dashboard')
        self.assertContains(response, 'PROF20260077')
        self.assertContains(response, curso)
        self.assertContains(response, disciplina.nome)
        self.assertContains(response, disciplina.codigo)
        self.assertContains(response, 'professor.dashboard@portaltech.com')

    def test_cadastro_usuario_regenera_senha_a_cada_abertura(self):
        with patch(
            'users.views.gerar_senha_inicial_aleatoria',
            side_effect=['SenhaPrimeiraA', 'SenhaSegundaB'],
        ):
            primeira_resposta = self.client.get(reverse('cadastrar_usuario_gestao'))
            segunda_resposta = self.client.get(reverse('cadastrar_usuario_gestao'))

        self.assertEqual(
            primeira_resposta.context['senha_inicial_aleatoria'],
            'SenhaPrimeiraA',
        )
        self.assertEqual(
            segunda_resposta.context['senha_inicial_aleatoria'],
            'SenhaSegundaB',
        )

    def test_gestao_pode_cadastrar_professor(self):
        get_response = self.client.get(reverse('cadastrar_usuario_gestao'))
        senha_inicial = get_response.context['senha_inicial_aleatoria']
        curso = cursos_disponiveis()[0]
        disciplina = disciplinas_do_curso(curso)[0]

        response = self.client.post(
            reverse('cadastrar_usuario_gestao'),
            {
                'role': Profile.ROLE_PROFESSOR,
                'nome': 'Professor Souza',
                'username': 'professor.souza',
                'email': 'souza@example.com',
                'password': 'senha-manual',
                'curso': curso,
                'disciplina': disciplina['codigo'],
            },
        )

        self.assertRedirects(response, reverse('dashboard_gestao'))
        professor = User.objects.get(first_name='Professor Souza')
        self.assertRegex(professor.username, r'^PROF\d{8}$')
        self.assertEqual(professor.email, gerar_email_institucional(professor.username))
        self.assertNotEqual(professor.email, 'souza@example.com')
        self.assertTrue(professor.check_password(senha_inicial))
        self.assertFalse(professor.check_password('senha-manual'))
        self.assertEqual(professor.profile.role, Profile.ROLE_PROFESSOR)
        self.assertEqual(professor.profile.matricula, professor.username)
        self.assertEqual(professor.profile.curso, curso)
        self.assertEqual(
            set(professor.profile.disciplinas.values_list('codigo', flat=True)),
            {disciplina['codigo']},
        )
        self.assertEqual(
            set(professor.profile.allowed_screens),
            {Profile.SCREEN_ALUNOS, Profile.SCREEN_NOTAS, Profile.SCREEN_FALTAS},
        )

    def test_telas_selecionadas_limitam_o_acesso(self):
        professor = User.objects.create_user(
            username='professor_notas',
            password='prof12345',
        )
        Profile.objects.create(
            user=professor,
            role=Profile.ROLE_PROFESSOR,
            allowed_screens=[Profile.SCREEN_NOTAS],
        )
        self.client.force_login(professor)

        notas_response = self.client.get(reverse('lista_notas'))
        faltas_response = self.client.get(reverse('lista_faltas'))

        self.assertEqual(notas_response.status_code, 200)
        self.assertEqual(faltas_response.status_code, 403)

    def test_portal_redireciona_para_primeira_tela_permitida(self):
        professor = User.objects.create_user(
            username='professor_portal',
            password='prof12345',
        )
        Profile.objects.create(
            user=professor,
            role=Profile.ROLE_PROFESSOR,
            allowed_screens=[Profile.SCREEN_FALTAS],
        )
        self.client.force_login(professor)

        response = self.client.get(reverse('portal'))

        self.assertRedirects(response, reverse('lista_faltas'))
