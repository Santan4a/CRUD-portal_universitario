import os

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404

from CRUD import settings
from alunos.models import Aluno
from disciplinas.models import Disciplina
from .models import Nota
from .forms import NotaForm
from users.access import can_manage_screen, filter_students_for_user, get_professor_discipline_ids, has_screen_access, is_aluno, is_professor, manage_screen_required
from users.models import Profile

from django.http import HttpResponse
from openpyxl import Workbook
from reportlab.pdfgen import canvas

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader

def disciplinas_por_aluno_json(user=None):
    alunos = Aluno.objects.prefetch_related('disciplinas').order_by('nome')
    discipline_ids = None

    if user:
        alunos = filter_students_for_user(user, alunos)
        if is_professor(user):
            discipline_ids = set(get_professor_discipline_ids(user))

    dados = {}

    for aluno in alunos:
        disciplinas_qs = aluno.disciplinas.all()
        if discipline_ids is not None:
            disciplinas_qs = disciplinas_qs.filter(id__in=discipline_ids)

        disciplinas = sorted(
            disciplinas_qs,
            key=lambda disciplina: (disciplina.nome, disciplina.codigo)
        )
        dados[str(aluno.id)] = [
            {
                'id': disciplina.id,
                'nome': disciplina.nome,
                'codigo': disciplina.codigo,
            }
            for disciplina in disciplinas
        ]

    return dados



def notas_permitidas_para_usuario(user):
    notas = Nota.objects.select_related('aluno', 'disciplina')

    if is_aluno(user):
        aluno = getattr(user, 'aluno', None)
        if not aluno:
            return Nota.objects.none()

        disciplina_ids = list(aluno.disciplinas.values_list('id', flat=True))
        return notas.filter(aluno=aluno, disciplina_id__in=disciplina_ids)

    if can_manage_screen(user, Profile.SCREEN_NOTAS):
        if is_professor(user):
            discipline_ids = get_professor_discipline_ids(user)
            return notas.filter(
                disciplina_id__in=discipline_ids,
                aluno__disciplinas__id__in=discipline_ids,
            ).distinct()

        return notas

    if has_screen_access(user, Profile.SCREEN_NOTAS):
        return Nota.objects.none()

    raise PermissionDenied


def disciplinas_exportaveis_para_usuario(user):
    notas = notas_permitidas_para_usuario(user)
    return Disciplina.objects.filter(
        id__in=notas.values('disciplina_id')
    ).order_by('nome', 'codigo').distinct()


# LISTAR
@login_required
def lista_notas(request):
    can_manage = can_manage_screen(request.user, Profile.SCREEN_NOTAS)
    can_delete = can_manage
    notas = notas_permitidas_para_usuario(request.user)

    return render(
        request,
        'notas/lista.html',
        {
            'notas': notas,
            'can_manage': can_manage,
            'can_delete': can_delete,
        }
    )


# CRIAR
@manage_screen_required(Profile.SCREEN_NOTAS)
def criar_nota(request):
    form = NotaForm(request.POST or None, user=request.user)

    if form.is_valid():
        form.save()
        return redirect('lista_notas')

    return render(
        request,
        'notas/form.html',
        {
            'form': form,
            'disciplinas_por_aluno': disciplinas_por_aluno_json(request.user),
        }
    )


# EDITAR
@manage_screen_required(Profile.SCREEN_NOTAS)
def editar_nota(request, id):
    nota = get_object_or_404(notas_permitidas_para_usuario(request.user), id=id)
    form = NotaForm(request.POST or None, instance=nota, user=request.user)

    if form.is_valid():
        form.save()
        return redirect('lista_notas')

    return render(
        request,
        'notas/form.html',
        {
            'form': form,
            'disciplinas_por_aluno': disciplinas_por_aluno_json(request.user),
        }
    )


# DELETAR
@manage_screen_required(Profile.SCREEN_NOTAS)
def deletar_nota(request, id):
    nota = get_object_or_404(notas_permitidas_para_usuario(request.user), id=id)

    if request.method == 'POST':
        nota.delete()
        return redirect('lista_notas')

    return render(request, 'notas/confirmar_exclusao.html', {'nota': nota})

# TELA DE EXPORTAÇÃO
@manage_screen_required(Profile.SCREEN_NOTAS)
def exportar_notas(request):

    disciplina_id = request.GET.get('disciplina')
    notas = None
    notas_permitidas = notas_permitidas_para_usuario(request.user)

    if disciplina_id:
        notas = notas_permitidas.filter(disciplina_id=disciplina_id)

    return render(
        request,
        'notas/exportar_notas.html',
        {
            'disciplinas': disciplinas_exportaveis_para_usuario(request.user),
            'notas': notas,
        }
    )

# EXPORTAR NOTAS
@manage_screen_required(Profile.SCREEN_NOTAS)
def exportar_pdf(request):

    disciplina_id = request.GET.get('disciplina')

    notas = notas_permitidas_para_usuario(request.user).filter(
        disciplina_id=disciplina_id
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        'attachment; filename="portal_tech_notas.pdf"'
    )

    pdf = canvas.Canvas(response, pagesize=letter)

    largura, altura = letter

    # LOGO
    logo_path = os.path.join(
        settings.BASE_DIR,
        'static',
        'assets',
        'brand',
        'logo_pdf.png'
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
    except:
        pass

    # TÍTULO
    pdf.setFont("Helvetica-Bold", 22)

    pdf.drawString(
        130,
        altura - 60,
        "PORTAL TECH"
    )

    # SUBTÍTULO
    pdf.setFont("Helvetica", 12)

    pdf.drawString(
        130,
        altura - 85,
        "Relatório Acadêmico de Notas"
    )

    # LINHA
    pdf.setStrokeColor(colors.HexColor("#0F172A"))

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
            'Aluno',
            'Disciplina',
            'N1',
            'N2',
            'Média'
        ]
    ]

    for nota in notas:

        dados.append([
            nota.aluno.nome,
            nota.disciplina.nome,
            nota.nota1,
            nota.nota2,
            round(nota.media(), 1)
        ])

    tabela = Table(
        dados,
        colWidths=[190, 190, 50, 50, 60]
    )

    tabela.setStyle(TableStyle([

    # CABEÇALHO
    ('BACKGROUND', (0, 0), (-1, 0),
     colors.HexColor("#0F172A")),

    ('TEXTCOLOR', (0, 0), (-1, 0),
     colors.white),

    ('FONTNAME', (0, 0), (-1, 0),
     'Helvetica-Bold'),

    ('FONTSIZE', (0, 0), (-1, 0),
     11),

    ('BOTTOMPADDING', (0, 0), (-1, 0),
     12),

    # CONTEÚDO
    ('BACKGROUND', (0, 1), (-1, -1),
     colors.whitesmoke),

    ('TEXTCOLOR', (0, 1), (-1, -1),
     colors.black),

    ('FONTNAME', (0, 1), (-1, -1),
     'Helvetica'),

    ('FONTSIZE', (0, 1), (-1, -1),
     9),

    # ALINHAMENTO
    ('ALIGN', (2, 1), (-1, -1),
     'CENTER'),

    ('VALIGN', (0, 0), (-1, -1),
     'MIDDLE'),

    # ESPAÇAMENTO
    ('TOPPADDING', (0, 1), (-1, -1),
     8),

    ('BOTTOMPADDING', (0, 1), (-1, -1),
     8),

    # LINHAS
    ('GRID', (0, 0), (-1, -1),
     1,
     colors.gray),

    ]))

    tabela.wrapOn(pdf, largura, altura)

    tabela.drawOn(
        pdf,
        40,
        altura - 400
    )

    # RODAPÉ
    pdf.setFont("Helvetica-Oblique", 9)

    pdf.drawString(
        40,
        30,
        "Portal TECH - Sistema Acadêmico"
    )

    pdf.save()

    return response

# EXPORTAR EXCEL
@manage_screen_required(Profile.SCREEN_NOTAS)
def exportar_excel(request):

    disciplina_id = request.GET.get('disciplina')

    notas = notas_permitidas_para_usuario(request.user).filter(
        disciplina_id=disciplina_id
    )

    workbook = Workbook()

    sheet = workbook.active

    sheet.title = 'Notas'

    sheet.append([
        'Aluno',
        'Disciplina',
        'Nota 1',
        'Nota 2',
        'Média'
    ])

    for nota in notas:

        sheet.append([
            nota.aluno.nome,
            nota.disciplina.nome,
            nota.nota1,
            nota.nota2,
            nota.media()
        ])

    response = HttpResponse(
        content_type=(
            'application/vnd.openxmlformats-'
            'officedocument.spreadsheetml.sheet'
        )
    )

    response['Content-Disposition'] = (
        'attachment; filename="notas.xlsx"'
    )

    workbook.save(response)

    return response