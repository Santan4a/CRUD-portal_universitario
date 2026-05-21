from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from alunos.models import Aluno
from disciplinas.catalogo import vincular_disciplinas_do_curso
from faltas.models import Falta
from notas.models import Nota
from users.models import Profile


class Command(BaseCommand):
    help = 'Create or reset the default portal users.'

    def handle(self, *args, **options):
        User = get_user_model()

        professor, _ = User.objects.get_or_create(
            username='professor',
            defaults={
                'email': 'professor@example.com',
                'first_name': 'Professor',
            },
        )
        professor.email = 'professor@example.com'
        professor.first_name = 'Professor'
        professor.is_staff = True
        professor.is_active = True
        professor.set_password('professor123')
        professor.save()

        Profile.objects.update_or_create(
            user=professor,
            defaults={'role': 'professor'},
        )

        gestao, _ = User.objects.get_or_create(
            username='gestao',
            defaults={
                'email': 'gestao@example.com',
                'first_name': 'Gestao',
            },
        )
        gestao.email = 'gestao@example.com'
        gestao.first_name = 'Gestao'
        gestao.is_staff = False
        gestao.is_active = True
        gestao.set_password('gestao123')
        gestao.save()

        Profile.objects.update_or_create(
            user=gestao,
            defaults={'role': 'gestao'},
        )

        aluno_user, _ = User.objects.get_or_create(
            username='aluno',
            defaults={
                'email': 'aluno@example.com',
                'first_name': 'Aluno',
            },
        )
        aluno_user.email = 'aluno@example.com'
        aluno_user.first_name = 'Aluno'
        aluno_user.is_staff = False
        aluno_user.is_active = True
        aluno_user.set_password('aluno123')
        aluno_user.save()

        Profile.objects.update_or_create(
            user=aluno_user,
            defaults={'role': 'aluno'},
        )

        aluno, _ = Aluno.objects.update_or_create(
            matricula='A001',
            defaults={
                'user': aluno_user,
                'nome': 'Aluno Demo',
                'curso': 'Bacharelado em Sistemas de Informação e Transformação Digital',
            },
        )
        disciplinas = vincular_disciplinas_do_curso(aluno)
        disciplina = disciplinas[0] if disciplinas else None

        if disciplina:
            Nota.objects.update_or_create(
                aluno=aluno,
                disciplina=disciplina,
                defaults={
                    'nota1': 8,
                    'nota2': 7,
                },
            )

            Falta.objects.get_or_create(
                aluno=aluno,
                disciplina=disciplina,
                data=date(2026, 5, 13),
                defaults={'justificada': False},
            )

        self.stdout.write(
            self.style.SUCCESS(
                'Default users ready: aluno/aluno123 and professor/professor123'
                ' and gestao/gestao123'
            )
        )
