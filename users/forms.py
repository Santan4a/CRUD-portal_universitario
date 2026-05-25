from django import forms
from django.contrib.auth.models import User

from alunos.models import Aluno
from disciplinas.catalogo import (
    curso_choices,
    disciplinas_do_curso,
    obter_ou_criar_disciplinas_do_curso,
    vincular_disciplinas_do_curso,
)
from users.models import Profile

from .access import get_default_screens_for_role
from .utils import (
    gerar_email_institucional,
    gerar_senha_inicial_aleatoria,
    gerar_usuario_aluno_unico,
    gerar_usuario_professor_unico,
)


class GestaoUsuarioForm(forms.Form):
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        label='Tipo de usuário',
    )
    nome = forms.CharField(
        label='Nome completo',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Nome completo'}),
    )
    username = forms.CharField(
        label='Usuário de acesso',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'usuario.login'}),
    )
    email = forms.EmailField(
        label='E-mail',
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'email@exemplo.com'}),
    )
    password = forms.CharField(
        label='Senha inicial',
        min_length=6,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Senha gerada automaticamente',
            'readonly': 'readonly',
        }),
    )
    curso = forms.ChoiceField(
        choices=[],
        label='Curso',
        required=False,
    )
    disciplina = forms.ChoiceField(
        choices=[],
        label='Disciplina que irá lecionar',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.initial_password = kwargs.pop(
            'initial_password',
            None
        ) or gerar_senha_inicial_aleatoria()
        super().__init__(*args, **kwargs)

        if self.is_bound:
            self.data = self.data.copy()
            self.data['password'] = self.initial_password

        role = self.initial.get('role') or self.data.get('role') or Profile.ROLE_ALUNO
        curso = self.data.get('curso') or self.initial.get('curso') or ''

        self.fields['role'].initial = role
        self.fields['curso'].choices = curso_choices()
        self.fields['disciplina'].choices = self._disciplina_choices(curso)
        self.fields['password'].initial = self.initial_password

    def _disciplina_choices(self, curso):
        choices = [('', 'Selecione uma disciplina')]
        choices.extend(
            (disciplina['codigo'], f"{disciplina['nome']} ({disciplina['codigo']})")
            for disciplina in disciplinas_do_curso(curso)
        )
        return choices

    def clean_username(self):
        return self.cleaned_data.get('username', '').strip()

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        curso = cleaned_data.get('curso')
        disciplina = cleaned_data.get('disciplina')
        cleaned_data['password'] = self.initial_password

        if role == Profile.ROLE_ALUNO:
            cleaned_data['username'] = gerar_usuario_aluno_unico(User, Profile, Aluno)
        elif role == Profile.ROLE_PROFESSOR:
            cleaned_data['username'] = gerar_usuario_professor_unico(User, Profile)
            cleaned_data['email'] = gerar_email_institucional(cleaned_data['username'])
        elif not cleaned_data.get('username'):
            self.add_error('username', 'Informe o usuário de acesso.')
        elif User.objects.filter(username=cleaned_data['username']).exists():
            self.add_error('username', 'Já existe um usuário com esse login.')

        if role in (Profile.ROLE_ALUNO, Profile.ROLE_PROFESSOR) and not curso:
            self.add_error('curso', 'Selecione o curso.')

        if role == Profile.ROLE_PROFESSOR and curso:
            codigos_do_curso = {
                item['codigo']
                for item in disciplinas_do_curso(curso)
            }

            if not disciplina:
                self.add_error('disciplina', 'Selecione a disciplina.')
            elif disciplina not in codigos_do_curso:
                self.add_error(
                    'disciplina',
                    'Selecione uma disciplina do curso informado.',
                )
        elif role != Profile.ROLE_PROFESSOR:
            cleaned_data['disciplina'] = ''

        return cleaned_data

    def save(self):
        role = self.cleaned_data['role']
        nome = self.cleaned_data['nome'].strip()
        username = self.cleaned_data['username']
        email = self.cleaned_data.get('email', '').strip()
        password = self.cleaned_data['password']
        allowed_screens = get_default_screens_for_role(role)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=nome,
        )
        profile_data = {
            'user': user,
            'role': role,
            'allowed_screens': list(allowed_screens),
        }

        if role in (Profile.ROLE_ALUNO, Profile.ROLE_PROFESSOR):
            profile_data['matricula'] = username
            profile_data['curso'] = self.cleaned_data['curso']

        profile = Profile.objects.create(**profile_data)

        if role == Profile.ROLE_PROFESSOR:
            disciplinas = obter_ou_criar_disciplinas_do_curso(
                self.cleaned_data['curso']
            )
            disciplina = next(
                item
                for item in disciplinas
                if item.codigo == self.cleaned_data['disciplina']
            )
            profile.disciplinas.set([disciplina])

        if role == Profile.ROLE_ALUNO:
            aluno = Aluno.objects.create(
                user=user,
                nome=nome,
                matricula=username,
                curso=self.cleaned_data['curso'],
            )
            vincular_disciplinas_do_curso(aluno)

        return user


class GestaoProfessorForm(forms.Form):
    nome = forms.CharField(
        label='Nome completo',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Nome completo'}),
    )
    email = forms.EmailField(
        label='E-mail',
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'email@exemplo.com'}),
    )
    curso = forms.ChoiceField(
        choices=[],
        label='Curso',
        required=False,
    )
    disciplina = forms.ChoiceField(
        choices=[],
        label='Disciplina que irá lecionar',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        disciplina_atual = self.instance.disciplinas.first()
        initial = kwargs.setdefault('initial', {})
        initial.setdefault(
            'nome',
            self.instance.user.get_full_name() or self.instance.user.first_name,
        )
        initial.setdefault('email', self.instance.user.email)
        initial.setdefault('curso', self.instance.curso)
        initial.setdefault(
            'disciplina',
            disciplina_atual.codigo if disciplina_atual else '',
        )
        super().__init__(*args, **kwargs)

        curso = self.data.get('curso') or self.initial.get('curso') or ''
        self.fields['email'].disabled = True
        self.fields['curso'].choices = curso_choices()
        self.fields['disciplina'].choices = self._disciplina_choices(curso)

    def _disciplina_choices(self, curso):
        choices = [('', 'Selecione uma disciplina')]
        choices.extend(
            (disciplina['codigo'], f"{disciplina['nome']} ({disciplina['codigo']})")
            for disciplina in disciplinas_do_curso(curso)
        )
        return choices

    def clean(self):
        cleaned_data = super().clean()
        curso = cleaned_data.get('curso')
        disciplina = cleaned_data.get('disciplina')

        if not curso:
            self.add_error('curso', 'Selecione o curso.')
            return cleaned_data

        codigos_do_curso = {
            item['codigo']
            for item in disciplinas_do_curso(curso)
        }

        if not disciplina:
            self.add_error('disciplina', 'Selecione a disciplina.')
        elif disciplina not in codigos_do_curso:
            self.add_error(
                'disciplina',
                'Selecione uma disciplina do curso informado.',
            )

        return cleaned_data

    def save(self):
        nome = self.cleaned_data['nome'].strip()
        curso = self.cleaned_data['curso']
        disciplina_codigo = self.cleaned_data['disciplina']

        user = self.instance.user
        user.first_name = nome
        user.last_name = ''
        user.save(update_fields=['first_name', 'last_name'])

        self.instance.curso = curso
        self.instance.save(update_fields=['curso'])

        disciplinas = obter_ou_criar_disciplinas_do_curso(curso)
        disciplina = next(
            item
            for item in disciplinas
            if item.codigo == disciplina_codigo
        )
        self.instance.disciplinas.set([disciplina])
        return self.instance


class GestaoGestorForm(forms.Form):
    nome = forms.CharField(
        label='Nome completo',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Nome completo'}),
    )
    username = forms.CharField(
        label='Usuário de acesso',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'usuario.login'}),
    )
    email = forms.EmailField(
        label='E-mail',
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'email@exemplo.com'}),
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        initial = kwargs.setdefault('initial', {})
        initial.setdefault(
            'nome',
            self.instance.user.get_full_name() or self.instance.user.first_name,
        )
        initial.setdefault('username', self.instance.user.username)
        initial.setdefault('email', self.instance.user.email)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.exclude(id=self.instance.user_id).filter(
            username=username
        ).exists():
            raise forms.ValidationError('Já existe um usuário com esse login.')
        return username

    def save(self):
        user = self.instance.user
        user.first_name = self.cleaned_data['nome'].strip()
        user.last_name = ''
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data.get('email', '').strip()
        user.save(update_fields=['first_name', 'last_name', 'username', 'email'])
        return self.instance
