from django import forms

from alunos.models import Aluno
from disciplinas.models import Disciplina
from users.access import filter_students_for_user, get_professor_discipline_ids, is_professor
from .models import Chamada, Falta, LimiteFaltas


class FaltaForm(forms.ModelForm):
    class Meta:
        model = Falta
        fields = ['aluno', 'disciplina', 'data', 'justificada']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['aluno'].queryset = self.obter_alunos_permitidos()
        self.fields['disciplina'].queryset = Disciplina.objects.none()
        self.fields['disciplina'].empty_label = 'Selecione um aluno primeiro'

        aluno = self.obter_aluno_selecionado()
        if aluno:
            self.fields['disciplina'].queryset = self.obter_disciplinas_permitidas(aluno)
            self.fields['disciplina'].empty_label = 'Selecione uma disciplina'

    def obter_alunos_permitidos(self):
        alunos = Aluno.objects.prefetch_related('disciplinas').order_by('nome')
        if self.user:
            alunos = filter_students_for_user(self.user, alunos)
        return alunos

    def obter_disciplinas_permitidas(self, aluno):
        disciplinas = aluno.disciplinas.order_by('nome', 'codigo')
        if self.user and is_professor(self.user):
            disciplinas = disciplinas.filter(
                id__in=get_professor_discipline_ids(self.user)
            )
        return disciplinas

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
            return self.fields['aluno'].queryset.get(pk=aluno_id)
        except (Aluno.DoesNotExist, TypeError, ValueError):
            return None


class ChamadaForm(forms.ModelForm):
    class Meta:
        model = Chamada
        fields = ['disciplina', 'data']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        disciplinas = Disciplina.objects.order_by('nome', 'codigo')

        if self.user and is_professor(self.user):
            disciplinas = disciplinas.filter(
                id__in=get_professor_discipline_ids(self.user)
            )

        self.fields['disciplina'].queryset = disciplinas


class LimiteFaltasForm(forms.ModelForm):
    class Meta:
        model = LimiteFaltas
        fields = ['disciplina', 'carga_horaria_total', 'percentual_maximo']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        disciplinas = Disciplina.objects.order_by('nome', 'codigo')

        if self.user and is_professor(self.user):
            disciplinas = disciplinas.filter(
                id__in=get_professor_discipline_ids(self.user)
            )

        self.fields['disciplina'].queryset = disciplinas
