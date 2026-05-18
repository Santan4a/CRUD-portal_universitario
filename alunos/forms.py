from django import forms
from .models import Aluno
from disciplinas.catalogo import curso_choices, vincular_disciplinas_do_curso


class AlunoForm(forms.ModelForm):

    class Meta:
        model = Aluno
        fields = ['user', 'nome', 'matricula', 'curso', 'disciplinas']


class GestaoAlunoForm(forms.ModelForm):
    curso = forms.ChoiceField(choices=[])

    class Meta:
        model = Aluno
        fields = ['nome', 'matricula', 'curso']
        labels = {
            'nome': 'Nome do aluno',
            'matricula': 'Matricula',
            'curso': 'Curso',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome completo'}),
            'matricula': forms.TextInput(attrs={'placeholder': 'Ex.: A002'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curso'].required = True
        self.fields['curso'].choices = curso_choices()

    def save(self, commit=True):
        aluno = super().save(commit=False)

        if commit:
            aluno.save()
            vincular_disciplinas_do_curso(aluno)

        return aluno
