from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import os
import json

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Aluno
from faltas.models import Falta
from notas.models import Nota
from cronograma.models import Cronograma
from users.access import can_manage_screen, is_aluno, is_professor, manage_screen_required
from users.models import Profile

from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from django.conf import settings

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

import os

from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

@manage_screen_required(Profile.SCREEN_ALUNOS)
def lista_alunos(request):
    alunos = Aluno.objects.all()
    return render(request, 'alunos/lista.html', {
        'alunos': alunos,
        'mostrar_acoes': False
    })


@login_required
def dashboard_aluno(request, id=None):

    if id is not None and can_manage_screen(request.user, Profile.SCREEN_ALUNOS):
        aluno = get_object_or_404(Aluno, id=id)
    elif is_aluno(request.user):
        aluno = get_object_or_404(Aluno, user=request.user)
    else:
        raise PermissionDenied

    notas = Nota.objects.filter(aluno=aluno)
    faltas = Falta.objects.filter(aluno=aluno)

    disciplina_ids = list(aluno.disciplinas.values_list('id', flat=True))

    if disciplina_ids:
        notas = notas.filter(disciplina_id__in=disciplina_ids)
        faltas = faltas.filter(disciplina_id__in=disciplina_ids)

    if notas.exists():
        media_geral = sum(n.media() for n in notas) / notas.count()
    else:
        media_geral = 0

    return render(request, 'alunos/dashboard.html', {
        'aluno': aluno,
        'media_geral': round(media_geral, 1),
        'disciplinas_cursando': notas.count(),
        'total_faltas': faltas.count(),
        'proxima_atividade': 'Verifique o calendário acadêmico',
    })


@login_required
def minha_area(request):

    if is_professor(request.user):
        return redirect('lista_alunos')

    if not is_aluno(request.user):
        raise PermissionDenied

    aluno = Aluno.objects.filter(user=request.user).first()

    notas = Nota.objects.none()
    faltas = Falta.objects.none()
    disciplinas = []
    media_geral = 0

    # cronograma estruturado por dia
    cronograma = {
        "Segunda": [],
        "Terça": [],
        "Quarta": [],
        "Quinta": [],
        "Sexta": [],
    }

    if aluno:
        disciplinas = list(aluno.disciplinas.all())
        disciplina_ids = [d.id for d in disciplinas]

        notas = Nota.objects.filter(
            aluno=aluno,
            disciplina_id__in=disciplina_ids
        )

        faltas = Falta.objects.filter(
            aluno=aluno,
            disciplina_id__in=disciplina_ids
        )

        cronograma_qs = Cronograma.objects.filter(
            disciplina_id__in=disciplina_ids
        ).select_related('disciplina')

        # ordenação correta
        ORDEM_DIAS = {
            "Segunda": 1,
            "Terça": 2,
            "Quarta": 3,
            "Quinta": 4,
            "Sexta": 5,
        }

        cronograma_ordenado = sorted(
            cronograma_qs,
            key=lambda x: (
                ORDEM_DIAS.get(x.get_dia_semana_display(), 99),
                x.horario_inicio
            )
        )

        for item in cronograma_ordenado:
            dia = item.get_dia_semana_display()

            if dia not in cronograma:
                cronograma[dia] = []

            cronograma[dia].append(item)

        if notas.exists():
            media_geral = sum(n.media() for n in notas) / notas.count()

    return render(request, 'alunos/minha_area.html', {
        'aluno': aluno,
        'notas': notas,
        'faltas': faltas,
        'disciplinas': disciplinas,
        'cronograma': cronograma,
        'media_geral': round(media_geral, 1),
    })


@login_required
def pagina_tutor_ia(request):
    return render(request, 'alunos/tutor_ia.html')


def criar_cliente_openai():
    from openai import OpenAI
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY não configurada.')

    return OpenAI(api_key=api_key)


@csrf_exempt
def tutor_ia(request):

    if request.method != 'POST':
        return JsonResponse({'resposta': 'Método não permitido.'}, status=405)

    try:
        data = json.loads(request.body)
        pergunta = data.get('mensagem')

        client = criar_cliente_openai()

        resposta = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um tutor especializado em tecnologia e programação."
                },
                {
                    "role": "user",
                    "content": pergunta
                }
            ]
        )

        texto = resposta.choices[0].message.content

        return JsonResponse({'resposta': texto})

    except Exception:
        return JsonResponse({'resposta': 'Tutor IA temporariamente indisponível.'})
    

@login_required
def exportar_notas_aluno(request):

    if not is_aluno(request.user):
        raise PermissionDenied

    aluno = get_object_or_404(
        Aluno,
        user=request.user
    )

    notas = Nota.objects.filter(
        aluno=aluno
    ).select_related(
        'aluno',
        'disciplina'
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        f'attachment; filename="boletim_{aluno.nome}.pdf"'
    )

    pdf = canvas.Canvas(
        response,
        pagesize=letter
    )

    largura, altura = letter

    # LOGO
    logo_path = os.path.join(
        settings.BASE_DIR,
        'static',
        'assets',
        'brand',
        'logo_pdf.png'
    )

    if os.path.exists(logo_path):
        pdf.drawImage(
            logo_path,
            40,
            altura - 110,
            width=70,
            height=70,
            preserveAspectRatio=True,
            mask='auto'
        )
    try:
        pdf.drawImage(
            logo_path,
            40,
            altura - 110,
            width=70,
            height=70,
            preserveAspectRatio=True,
            mask='auto'
        )
    except Exception:
        pass

    # TÍTULO
    pdf.setFont(
        "Helvetica-Bold",
        22
    )

    pdf.drawString(
        130,
        altura - 60,
        "PORTAL TECH"
    )

    # SUBTÍTULO
    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawString(
        130,
        altura - 85,
        f"Boletim Acadêmico - {aluno.nome}"
    )

    # LINHA
    pdf.setStrokeColor(
        colors.HexColor("#0F172A")
    )

    pdf.setLineWidth(2)

    pdf.line(
        40,
        altura - 125,
        largura - 40,
        altura - 125
    )

    # TABELA
    dados = [
        [
            'Disciplina',
            'N1',
            'N2',
            'Média',
            'Situação'
        ]
    ]

    for nota in notas:

        media = round(
            nota.media(),
            1
        )

        situacao = (
            'Aprovado'
            if media >= 7
            else 'Revisar'
        )

        dados.append([
            nota.disciplina.nome,
            nota.nota1,
            nota.nota2,
            media,
            situacao
        ])

    tabela = Table(
        dados,
        colWidths=[220, 60, 60, 70, 100]
    )

    tabela.setStyle(TableStyle([

        ('BACKGROUND',
         (0, 0),
         (-1, 0),
         colors.HexColor("#0F172A")),

        ('TEXTCOLOR',
         (0, 0),
         (-1, 0),
         colors.white),

        ('FONTNAME',
         (0, 0),
         (-1, 0),
         'Helvetica-Bold'),

        ('FONTSIZE',
         (0, 0),
         (-1, 0),
         11),

        ('BOTTOMPADDING',
         (0, 0),
         (-1, 0),
         12),

        ('BACKGROUND',
         (0, 1),
         (-1, -1),
         colors.whitesmoke),

        ('GRID',
         (0, 0),
         (-1, -1),
         1,
         colors.gray),

        ('ALIGN',
         (1, 1),
         (-1, -1),
         'CENTER'),

        ('VALIGN',
         (0, 0),
         (-1, -1),
         'MIDDLE'),
    ]))

    tabela.wrapOn(
        pdf,
        largura,
        altura
    )

    tabela.drawOn(
        pdf,
        40,
        altura - 350
    )

    # RODAPÉ
    pdf.setFont(
        "Helvetica-Oblique",
        9
    )

    pdf.drawString(
        40,
        30,
        "Portal TECH - Sistema Acadêmico"
    )

    pdf.save()

    return response