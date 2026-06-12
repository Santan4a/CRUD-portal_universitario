from datetime import date, time

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from cronograma.models import Cronograma
from disciplinas.catalogo import cursos_disponiveis, disciplinas_do_curso
from disciplinas.models import Disciplina
from faltas.models import Falta
from notas.models import Nota
from users.models import Profile
from .forms import GestaoAlunoForm
from .models import Aluno


class AlunoUrlTests(SimpleTestCase):
    def test_aluno_crud_urls_are_registered(self):
        self.assertEqual(reverse('minha_area'), '/alunos/minha-area/')
        self.assertEqual(reverse('lista_alunos'), '/alunos/')
        self.assertEqual(reverse('dashboard_aluno', args=[1]), '/alunos/dashboard/1/')
        self.assertEqual(
            reverse('editar_aluno_gestao', args=[1]),
            '/gestao/alunos/1/editar/'
        )

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_home_renders_login(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Acessar portal')


@override_settings(SECURE_SSL_REDIRECT=False)
class AlunoPageRenderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='professor_teste',
            password='admin12345'
        )
        self.professor_profile = Profile.objects.create(user=self.user, role='professor')
        self.disciplina_professor = Disciplina.objects.create(
            nome='Matematica',
            codigo='MAT-PROF',
        )
        self.professor_profile.disciplinas.add(self.disciplina_professor)
        self.client.force_login(self.user)

    def test_lista_alunos_renders_successfully(self):
        aluno = Aluno.objects.create(nome='Ana Silva', matricula='A101')
        aluno.disciplinas.add(self.disciplina_professor)

        response = self.client.get(reverse('lista_alunos'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ana Silva')

    def test_dashboard_aluno_renders_successfully(self):
        aluno = Aluno.objects.create(nome='Ana Silva', matricula='A102')
        aluno.disciplinas.add(self.disciplina_professor)

        response = self.client.get(reverse('dashboard_aluno', args=[aluno.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard de Ana Silva')

    def test_lista_alunos_requires_login(self):
        self.client.logout()

        response = self.client.get(reverse('lista_alunos'))

        self.assertRedirects(response, '/?next=/alunos/')

    def test_student_is_redirected_to_own_area_from_portal(self):
        aluno_user = User.objects.create_user(
            username='aluno_portal_teste',
            password='aluno12345'
        )
        Profile.objects.create(user=aluno_user, role='aluno')
        Aluno.objects.create(
            user=aluno_user,
            nome='Ana Silva',
            matricula='A103',
            curso='Bacharelado em Sistemas de Informação e Transformação Digital'
        )
        self.client.force_login(aluno_user)

        response = self.client.get(reverse('portal'))

        self.assertRedirects(response, reverse('minha_area'))

    def test_minha_area_mostra_apenas_registros_do_curso_atual(self):
        curso_atual, curso_antigo = cursos_disponiveis()[:2]
        disciplina_atual_dados = disciplinas_do_curso(curso_atual)[0]
        disciplina_antiga_dados = disciplinas_do_curso(curso_antigo)[0]
        disciplina_atual = Disciplina.objects.create(**disciplina_atual_dados)
        disciplina_antiga = Disciplina.objects.create(**disciplina_antiga_dados)
        aluno_user = User.objects.create_user(
            username='aluno_area_teste',
            password='aluno12345'
        )
        Profile.objects.create(user=aluno_user, role='aluno')
        aluno = Aluno.objects.create(
            user=aluno_user,
            nome='Ana Silva',
            matricula='A104',
            curso=curso_atual
        )
        aluno.disciplinas.add(disciplina_atual)
        Nota.objects.create(
            aluno=aluno,
            disciplina=disciplina_atual,
            nota1=9,
            nota2=8
        )
        Nota.objects.create(
            aluno=aluno,
            disciplina=disciplina_antiga,
            nota1=6,
            nota2=5
        )
        Falta.objects.create(
            aluno=aluno,
            disciplina=disciplina_antiga,
            data=date(2026, 5, 13)
        )
        self.client.force_login(aluno_user)

        response = self.client.get(reverse('minha_area'))

        self.assertContains(response, disciplina_atual.nome)
        self.assertNotContains(response, disciplina_antiga.nome)

    def test_minha_area_filtra_cronograma_pelo_turno_do_aluno(self):
        curso = cursos_disponiveis()[0]
        disciplina_dados = disciplinas_do_curso(curso)[0]
        disciplina = Disciplina.objects.create(**disciplina_dados)
        aluno_user = User.objects.create_user(
            username='aluno_turno_cronograma',
            password='aluno12345',
        )
        Profile.objects.create(user=aluno_user, role='aluno')
        aluno = Aluno.objects.create(
            user=aluno_user,
            nome='Ana Turno',
            matricula='A105',
            curso=curso,
            turno=Aluno.TURNO_MANHA,
        )
        aluno.disciplinas.add(disciplina)
        Cronograma.objects.create(
            disciplina=disciplina,
            dia_semana='SEG',
            turno=Aluno.TURNO_MANHA,
            horario_inicio=time(7, 30),
            horario_fim=time(9, 10),
            sala='MANHA-01',
        )
        Cronograma.objects.create(
            disciplina=disciplina,
            dia_semana='SEG',
            turno=Aluno.TURNO_TARDE,
            horario_inicio=time(13, 30),
            horario_fim=time(15, 10),
            sala='TARDE-01',
        )
        self.client.force_login(aluno_user)

        response = self.client.get(reverse('minha_area'))

        self.assertContains(response, '07:30')
        self.assertContains(response, 'Manhã')
        self.assertNotContains(response, '13:30')
        self.assertNotContains(response, 'Tarde')

    def test_tutor_ia_requer_aluno_logado(self):
        professor = User.objects.create_user(
            username='professor_tutor_bloqueado',
            password='prof12345',
        )
        Profile.objects.create(user=professor, role='professor')
        self.client.force_login(professor)

        response = self.client.get(reverse('pagina_tutor_ia'))

        self.assertEqual(response.status_code, 403)

    def test_student_cannot_access_aluno_crud(self):
        aluno_user = User.objects.create_user(
            username='aluno_bloqueado_teste',
            password='aluno12345'
        )
        Profile.objects.create(user=aluno_user, role='aluno')
        self.client.force_login(aluno_user)

        response = self.client.get(reverse('lista_alunos'))

        self.assertEqual(response.status_code, 403)


class AlunoMatriculaTests(TestCase):
    def test_aluno_sem_matricula_recebe_proxima_sequencia(self):
        Aluno.objects.all().delete()
        ano = timezone.localdate().year

        primeiro = Aluno.objects.create(nome='Ana Silva')
        segundo = Aluno.objects.create(nome='Bruno Lima')

        self.assertEqual(primeiro.matricula, f'ALU{ano}0001')
        self.assertEqual(segundo.matricula, f'ALU{ano}0002')

    def test_matricula_automatica_continua_a_maior_existente(self):
        ano = timezone.localdate().year
        Aluno.objects.create(nome='Ana Silva', matricula=f'ALU{ano}0009')

        aluno = Aluno.objects.create(nome='Bruno Lima')

        self.assertEqual(aluno.matricula, f'ALU{ano}0010')


class GestaoAlunoFormTests(TestCase):
    def test_salvar_aluno_vincula_disciplinas_do_curso_json(self):
        curso = 'Bacharelado em Sistemas de Informação e Transformação Digital'
        form = GestaoAlunoForm(data={
            'nome': 'Bruno Lima',
            'curso': curso,
            'turno': Aluno.TURNO_NOITE,
        })

        self.assertTrue(form.is_valid())

        aluno = form.save()
        codigos_esperados = {
            disciplina['codigo']
            for disciplina in disciplinas_do_curso(curso)
        }

        self.assertEqual(
            set(aluno.disciplinas.values_list('codigo', flat=True)),
            codigos_esperados,
        )
        self.assertEqual(
            Disciplina.objects.filter(codigo__in=codigos_esperados).count(),
            len(codigos_esperados),
        )
        self.assertEqual(aluno.turno, Aluno.TURNO_NOITE)
        self.assertRegex(aluno.matricula, r'^ALU\d{8}$')

    def test_formulario_exige_turno_do_aluno(self):
        curso = cursos_disponiveis()[0]
        form = GestaoAlunoForm(data={
            'nome': 'Bruno Lima',
            'curso': curso,
        })

        self.assertFalse(form.is_valid())
        self.assertIn('turno', form.errors)

    def test_curso_do_formulario_vem_da_matriz_json(self):
        form = GestaoAlunoForm()
        cursos = {valor for valor, _ in form.fields['curso'].choices}

        self.assertIn('Bacharelado em Sistemas de Informação e Transformação Digital', cursos)


@override_settings(SECURE_SSL_REDIRECT=False)
class GestaoAlunoViewTests(TestCase):
    def setUp(self):
        self.gestao_user = User.objects.create_user(
            username='gestao_teste',
            password='gestao12345'
        )
        Profile.objects.create(user=self.gestao_user, role='gestao')
        self.client.force_login(self.gestao_user)

    def test_dashboard_exibe_link_para_editar_aluno(self):
        aluno = Aluno.objects.create(nome='Ana Silva')

        response = self.client.get(reverse('dashboard_gestao'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse('editar_aluno_gestao', args=[aluno.id])
        )

    def test_edicao_aluno_define_tipo_padrao_para_exibir_curso(self):
        curso = cursos_disponiveis()[0]
        aluno = Aluno.objects.create(nome='Ana Silva', curso=curso)

        response = self.client.get(reverse('editar_aluno_gestao', args=[aluno.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'const tipoPadraoUsuario = \"aluno\";')
        self.assertContains(response, 'id="id_curso"')
        self.assertContains(response, 'id="id_turno"')

    def test_edicao_aluno_sincroniza_usuario_e_profile(self):
        curso_antigo, curso_novo = cursos_disponiveis()[:2]
        aluno_user = User.objects.create_user(
            username='aluno.editar.sync',
            password='aluno12345',
            first_name='Nome Antigo',
            email='antigo@example.com',
        )
        profile = Profile.objects.create(
            user=aluno_user,
            role='aluno',
            curso=curso_antigo,
            turno=Aluno.TURNO_MANHA,
            matricula='ALU20269999',
        )
        aluno = Aluno.objects.create(
            user=aluno_user,
            nome='Nome Antigo',
            matricula='ALU20269999',
            curso=curso_antigo,
            turno=Aluno.TURNO_MANHA,
        )

        response = self.client.post(
            reverse('editar_aluno_gestao', args=[aluno.id]),
            {
                'nome': 'Nome Novo',
                'curso': curso_novo,
                'turno': Aluno.TURNO_TARDE,
                'email': 'novo@example.com',
            },
        )

        self.assertRedirects(response, reverse('dashboard_gestao'))
        aluno.refresh_from_db()
        aluno_user.refresh_from_db()
        profile.refresh_from_db()
        self.assertEqual(aluno.nome, 'Nome Novo')
        self.assertEqual(aluno_user.first_name, 'Nome Novo')
        self.assertEqual(aluno_user.email, 'novo@example.com')
        self.assertEqual(aluno.turno, Aluno.TURNO_TARDE)
        self.assertEqual(profile.curso, curso_novo)
        self.assertEqual(profile.turno, Aluno.TURNO_TARDE)

    def test_gestao_pode_alterar_curso_do_aluno(self):
        curso_antigo, curso_novo = cursos_disponiveis()[:2]
        disciplina_antiga_dados = disciplinas_do_curso(curso_antigo)[0]
        disciplina_antiga = Disciplina.objects.create(**disciplina_antiga_dados)
        aluno = Aluno.objects.create(
            nome='Ana Silva',
            curso=curso_antigo,
            turno=Aluno.TURNO_MANHA,
        )
        Nota.objects.create(
            aluno=aluno,
            disciplina=disciplina_antiga,
            nota1=8,
            nota2=7
        )
        Falta.objects.create(
            aluno=aluno,
            disciplina=disciplina_antiga,
            data=date(2026, 5, 13)
        )

        response = self.client.post(
            reverse('editar_aluno_gestao', args=[aluno.id]),
            {
                'nome': aluno.nome,
                'curso': curso_novo,
                'turno': Aluno.TURNO_MANHA,
            },
        )

        aluno.refresh_from_db()
        codigos_esperados = {
            disciplina['codigo']
            for disciplina in disciplinas_do_curso(curso_novo)
        }

        self.assertRedirects(response, reverse('dashboard_gestao'))
        self.assertEqual(aluno.curso, curso_novo)
        self.assertEqual(
            set(aluno.disciplinas.values_list('codigo', flat=True)),
            codigos_esperados,
        )
        self.assertFalse(Nota.objects.filter(
            aluno=aluno,
            disciplina=disciplina_antiga
        ).exists())
        self.assertFalse(Falta.objects.filter(
            aluno=aluno,
            disciplina=disciplina_antiga
        ).exists())

