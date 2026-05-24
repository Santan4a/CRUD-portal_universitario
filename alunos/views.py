from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import os
import json

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Aluno
from .forms import AlunoForm
from faltas.models import Falta
from notas.models import Nota
from users.access import can_manage_screen, is_aluno, is_professor, manage_screen_required
from users.models import Profile


def criar_cliente_openai():
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:
        load_dotenv = None

    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:
        raise RuntimeError('A biblioteca openai não está instalada.') from exc

    if load_dotenv:
        load_dotenv()

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY não configurada.')

    return OpenAI(api_key=api_key)


def resposta_tutor_indisponivel():
    return JsonResponse({
        'resposta': (
            'Tutor IA temporariamente indisponível. '
            'Verifique a configuração da API OpenAI.'
        )
    })


@manage_screen_required(Profile.SCREEN_ALUNOS)
def lista_alunos(request):
    alunos = Aluno.objects.all()

    context = {
        'alunos': alunos,
        'mostrar_acoes': False
    }

    return render(request, 'alunos/lista.html', context)


@login_required
def dashboard_aluno(request, id):
    aluno = get_object_or_404(Aluno, id=id)

    if is_aluno(request.user):
        if aluno.user_id != request.user.id:
            raise PermissionDenied
    elif not (
        can_manage_screen(request.user, Profile.SCREEN_ALUNOS)
        or can_manage_screen(request.user, Profile.SCREEN_GESTAO)
    ):
        raise PermissionDenied
    
    notas = Nota.objects.filter(aluno=aluno)
    faltas = Falta.objects.filter(aluno=aluno)
    disciplina_ids = list(aluno.disciplinas.values_list('id', flat=True))

    if disciplina_ids:
        notas = notas.filter(disciplina_id__in=disciplina_ids)
        faltas = faltas.filter(disciplina_id__in=disciplina_ids)
    
    if notas.exists():
        soma_medias = sum([nota.media() for nota in notas])
        media_geral = soma_medias / notas.count()
    else:
        media_geral = 0
    
    context = {
        'aluno': aluno,
        'media_geral': round(media_geral, 1),
        'disciplinas_cursando': notas.count(),
        'total_faltas': faltas.count(),
        'proxima_atividade': 'Verifique o calendário acadêmico',
    }
    
    return render(request, 'alunos/dashboard.html', context)


@login_required
def minha_area(request):
    if is_professor(request.user):
        return redirect('lista_alunos')

    if not is_aluno(request.user):
        raise PermissionDenied

    aluno = Aluno.objects.filter(user=request.user).prefetch_related('disciplinas').first()
    notas = Nota.objects.none()
    faltas = Falta.objects.none()
    disciplinas = []
    media_geral = 0

    if aluno:
        notas = Nota.objects.filter(aluno=aluno).select_related('disciplina')
        faltas = Falta.objects.filter(aluno=aluno).select_related('disciplina')
        disciplinas = list(aluno.disciplinas.all())

        if disciplinas:
            disciplina_ids = [disciplina.id for disciplina in disciplinas]
            notas = notas.filter(disciplina_id__in=disciplina_ids)
            faltas = faltas.filter(disciplina_id__in=disciplina_ids)
        else:
            disciplinas = [nota.disciplina for nota in notas]

        if notas.exists():
            media_geral = round(
                sum(nota.media() for nota in notas) / notas.count(),
                1
            )

    context = {
        'aluno': aluno,
        'notas': notas,
        'faltas': faltas,
        'disciplinas': disciplinas,
        'media_geral': media_geral,
    }

    return render(request, 'alunos/minha_area.html', context)

@login_required
def pagina_tutor_ia(request):

    return render(
        request,
        'alunos/tutor_ia.html'
    )

@csrf_exempt
def tutor_ia(request):

    if request.method == 'POST':

        try:

            data = json.loads(request.body)

            pergunta = data.get('mensagem')

            client = criar_cliente_openai()

            resposta = client.chat.completions.create(

                model="gpt-4.1-mini",

                messages=[

                    {
                        "role": "system",
                        "content": """
                        Você é um tutor especializado
                        em tecnologia e programação.
                        """
                    },

                    {
                        "role": "user",
                        "content": pergunta
                    }
                ]
            )

            texto = resposta.choices[0].message.content

            return JsonResponse({
                'resposta': texto
            })

        except Exception:

            return resposta_tutor_indisponivel()

    return JsonResponse({
        'resposta': 'Método não permitido.'
    }, status=405)
