from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_default_gestao_user(apps, schema_editor):
    user_app_label, user_model_name = settings.AUTH_USER_MODEL.split('.')
    User = apps.get_model(user_app_label, user_model_name)
    Profile = apps.get_model('users', 'Profile')

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
    gestao.password = make_password('gestao123')
    gestao.save()

    Profile.objects.update_or_create(
        user=gestao,
        defaults={'role': 'gestao'},
    )


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_create_default_portal_users'),
    ]

    operations = [
        migrations.RunPython(
            create_default_gestao_user,
            migrations.RunPython.noop,
        ),
    ]
