# Generated to add teaching course data to profiles.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('disciplinas', '0003_alter_disciplina_id'),
        ('users', '0006_profile_allowed_screens'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='curso',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='profile',
            name='disciplinas',
            field=models.ManyToManyField(
                blank=True,
                related_name='professores',
                to='disciplinas.disciplina',
                verbose_name='disciplinas lecionadas',
            ),
        ),
    ]
