# Generated to align the Profile role choices with the gestao area.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_create_default_gestao_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(
                choices=[
                    ('aluno', 'Aluno'),
                    ('professor', 'Professor'),
                    ('gestao', 'gestao'),
                ],
                max_length=20,
            ),
        ),
    ]
