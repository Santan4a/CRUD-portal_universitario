from django import forms
from .models import Aluno
from disciplinas.catalogo import curso_choices, vincular_disciplinas_do_curso


class AlunoForm(forms.ModelForm):

    class Meta:
        model = Aluno
        fields = ['user', 'nome', 'curso', 'disciplinas']


class GestaoAlunoForm(forms.ModelForm):
    curso = forms.ChoiceField(choices=[])

    class Meta:
        model = Aluno
        fields = ['nome', 'curso']
        labels = {
            'nome': 'Nome do aluno',
            'curso': 'Curso',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome completo'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curso'].required = True
        self.fields['curso'].choices = curso_choices()

    def save(self, commit=True):
        aluno = super().save(commit=False)

        if commit:
            aluno.save()
            disciplinas = vincular_disciplinas_do_curso(aluno)
            self.remover_registros_fora_do_curso(aluno, disciplinas)

        return aluno

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
