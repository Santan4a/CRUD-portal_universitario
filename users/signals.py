from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Profile
from .utils import gerar_matricula_unica


@receiver(pre_save, sender=Profile)
def preencher_matricula_profile(sender, instance, **kwargs):
    if instance.matricula:
        return

    instance.matricula = gerar_matricula_unica(instance.role, sender)