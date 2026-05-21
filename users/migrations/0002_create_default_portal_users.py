from datetime import date

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_default_portal_users(apps, schema_editor):
    user_app_label, user_model_name = settings.AUTH_USER_MODEL.split('.')
    User = apps.get_model(user_app_label, user_model_name)
    Profile = apps.get_model('users', 'Profile')
    Aluno = apps.get_model('alunos', 'Aluno')
    Disciplina = apps.get_model('disciplinas', 'Disciplina')
    Nota = apps.get_model('notas', 'Nota')
    Falta = apps.get_model('faltas', 'Falta')

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
    professor.password = make_password('professor123')
    professor.save()

    Profile.objects.update_or_create(
        user=professor,
        defaults={'role': 'professor'},
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
    aluno_user.password = make_password('aluno123')
    aluno_user.save()

    Profile.objects.update_or_create(
        user=aluno_user,
        defaults={'role': 'aluno'},
    )

    disciplina, _ = Disciplina.objects.get_or_create(
        codigo='MAT01',
        defaults={'nome': 'Matemática'},
    )

    aluno, _ = Aluno.objects.update_or_create(
        matricula='A001',
        defaults={
            'user': aluno_user,
            'nome': 'Aluno Demo',
            'curso': 'Bacharelado em Sistemas de Informação e Transformação Digital',
        },
    )
    aluno.disciplinas.add(disciplina)

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


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('alunos', '0005_aluno_curso_aluno_disciplinas_aluno_user'),
        ('disciplinas', '0003_alter_disciplina_id'),
        ('faltas', '0001_initial'),
        ('notas', '0002_rename_valor_nota_nota1_nota_nota2_and_more'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_portal_users, migrations.RunPython.noop),
    ]
