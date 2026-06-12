from django import forms
from .models import Aluno
from disciplinas.catalogo import curso_choices, vincular_disciplinas_do_curso


class AlunoForm(forms.ModelForm):

    class Meta:
        model = Aluno
        fields = ['user', 'nome', 'curso', 'disciplinas']


class GestaoAlunoForm(forms.ModelForm):
    curso = forms.ChoiceField(choices=[])
    turno = forms.ChoiceField(
        choices=[],
        label='Turno',
    )
    email = forms.EmailField(
        label='E-mail',
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'email@exemplo.com'}),
    )

    class Meta:
        model = Aluno
        fields = ['nome', 'curso', 'turno', 'email']
        labels = {
            'nome': 'Nome do aluno',
            'curso': 'Curso',
            'turno': 'Turno',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome completo'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curso'].required = True
        self.fields['curso'].choices = curso_choices()
        self.fields['turno'].required = True
        self.fields['turno'].choices = [('', 'Selecione um turno'), *Aluno.TURNO_CHOICES]

        if self.instance and self.instance.user_id:
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        aluno = super().save(commit=False)

        if commit:
            aluno.save()
            self.sincronizar_usuario(aluno)
            disciplinas = vincular_disciplinas_do_curso(aluno)
            self.remover_registros_fora_do_curso(aluno, disciplinas)

        return aluno

    def sincronizar_usuario(self, aluno):
        if not aluno.user_id:
            return

        user = aluno.user
        user.first_name = aluno.nome
        user.last_name = ''
        user.email = (self.cleaned_data.get('email') or '').strip()
        user.save(update_fields=['first_name', 'last_name', 'email'])

        profile = getattr(user, 'profile', None)
        if profile:
            profile.curso = aluno.curso
            profile.turno = aluno.turno
            if not profile.matricula:
                profile.matricula = aluno.matricula
            profile.save(update_fields=['curso', 'turno', 'matricula'])

    def remover_registros_fora_do_curso(self, aluno, disciplinas):
        from faltas.models import Falta
        from notas.models import Nota

        disciplina_ids = [disciplina.id for disciplina in disciplinas]
        Nota.objects.filter(aluno=aluno).exclude(
            disciplina_id__in=disciplina_ids
        ).delete()
        Falta.objects.filter(aluno=aluno).exclude(
            disciplina_id__in=disciplina_ids
        ).delete()
