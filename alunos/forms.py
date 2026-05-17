from django import forms
from .models import Aluno


class AlunoForm(forms.ModelForm):

    class Meta:
        model = Aluno
        fields = ['user', 'nome', 'matricula', 'curso', 'disciplinas']


class GestaoAlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome', 'matricula', 'curso', 'disciplinas']
        labels = {
            'nome': 'Nome do aluno',
            'matricula': 'Matricula',
            'curso': 'Curso',
            'disciplinas': 'Disciplinas',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome completo'}),
            'matricula': forms.TextInput(attrs={'placeholder': 'Ex.: A002'}),
            'curso': forms.TextInput(attrs={'placeholder': 'Ex.: Sistemas de Informacao'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curso'].required = True
