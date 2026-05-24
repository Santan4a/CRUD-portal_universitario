# Generated to add configurable screen permissions to profiles.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_profile_matricula_alter_profile_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='allowed_screens',
            field=models.JSONField(
                blank=True,
                default=None,
                null=True,
                verbose_name='telas permitidas',
            ),
        ),
    ]
