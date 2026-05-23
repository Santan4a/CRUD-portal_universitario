from django import forms

from alunos.models import Aluno
from disciplinas.models import Disciplina
from .models import Nota


class NotaForm(forms.ModelForm):

    class Meta:
        model = Nota
        fields = ['aluno', 'disciplina', 'nota1', 'nota2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['disciplina'].queryset = Disciplina.objects.none()
        self.fields['disciplina'].empty_label = 'Selecione um aluno primeiro'

        aluno = self.obter_aluno_selecionado()

        if aluno:
            self.fields['disciplina'].queryset = aluno.disciplinas.order_by(
                'nome',
                'codigo'
            )
            self.fields['disciplina'].empty_label = 'Selecione uma disciplina'

    def obter_aluno_selecionado(self):
        aluno_id = None
        aluno_inicial = self.initial.get('aluno')

        if self.is_bound:
            aluno_id = self.data.get(self.add_prefix('aluno'))
        elif self.instance and self.instance.pk:
            aluno_id = self.instance.aluno_id
        elif isinstance(aluno_inicial, Aluno):
            return aluno_inicial
        elif aluno_inicial:
            aluno_id = aluno_inicial

        if not aluno_id:
            return None

        try:
            return Aluno.objects.prefetch_related('disciplinas').get(pk=aluno_id)
        except (Aluno.DoesNotExist, TypeError, ValueError):
            return None

    def clean(self):
        cleaned_data = super().clean()

        nota1 = cleaned_data.get("nota1")
        nota2 = cleaned_data.get("nota2")

        for nota in [nota1, nota2]:
            if nota is not None and (nota < 0 or nota > 10):
                raise forms.ValidationError("Notas devem estar entre 0 e 10.")

        return cleaned_data
