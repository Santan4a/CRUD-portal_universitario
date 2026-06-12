from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from alunos.models import Aluno
from users.access import (
    can_manage_screen,
    filter_students_for_user,
    get_professor_discipline_ids,
    has_screen_access,
    is_aluno,
    is_professor,
    manage_screen_required,
)
from users.models import Profile
from .forms import ChamadaForm, FaltaForm, LimiteFaltasForm
from .models import Chamada, Falta, LimiteFaltas, PresencaChamada


def disciplinas_por_aluno_json(user=None):
    alunos = Aluno.objects.prefetch_related('disciplinas').order_by('nome')
    discipline_ids = None

    if user:
        alunos = filter_students_for_user(user, alunos)
        if is_professor(user):
            discipline_ids = set(get_professor_discipline_ids(user))

    dados = {}

    for aluno in alunos:
        disciplinas = aluno.disciplinas.all()
        if discipline_ids is not None:
            disciplinas = disciplinas.filter(id__in=discipline_ids)

        dados[str(aluno.id)] = [
            {
                'id': disciplina.id,
                'nome': disciplina.nome,
                'codigo': disciplina.codigo,
            }
            for disciplina in disciplinas.order_by('nome', 'codigo')
        ]

    return dados


def faltas_permitidas_para_usuario(user):
    faltas = Falta.objects.select_related('aluno', 'disciplina')

    if is_aluno(user):
        aluno = getattr(user, 'aluno', None)
        if not aluno:
            return Falta.objects.none()

        disciplina_ids = list(aluno.disciplinas.values_list('id', flat=True))
        return faltas.filter(aluno=aluno, disciplina_id__in=disciplina_ids)

    if can_manage_screen(user, Profile.SCREEN_FALTAS):
        if is_professor(user):
            discipline_ids = get_professor_discipline_ids(user)
            return faltas.filter(
                disciplina_id__in=discipline_ids,
                aluno__disciplinas__id__in=discipline_ids,
            ).distinct()

        return faltas

    if has_screen_access(user, Profile.SCREEN_FALTAS):
        return Falta.objects.none()

    raise PermissionDenied


def limites_permitidos_para_usuario(user):
    limites = LimiteFaltas.objects.select_related('disciplina').order_by(
        'disciplina__nome',
        'disciplina__codigo',
    )

    if is_professor(user):
        limites = limites.filter(disciplina_id__in=get_professor_discipline_ids(user))

    return limites


def alertas_limite_faltas(faltas):
    contagens = faltas.values(
        'aluno__nome',
        'aluno__matricula',
        'disciplina_id',
        'disciplina__nome',
        'disciplina__codigo',
    ).annotate(total=Count('id')).order_by('-total')
    limites = {
        limite.disciplina_id: limite
        for limite in LimiteFaltas.objects.filter(
            disciplina_id__in=[item['disciplina_id'] for item in contagens]
        )
    }
    alertas = []

    for item in contagens:
        limite = limites.get(item['disciplina_id'])
        if not limite or limite.faltas_maximas <= 0:
            continue

        percentual = (item['total'] / limite.faltas_maximas) * 100
        if percentual >= 80:
            alertas.append({
                'aluno': item['aluno__nome'],
                'matricula': item['aluno__matricula'],
                'disciplina': item['disciplina__nome'],
                'codigo': item['disciplina__codigo'],
                'faltas': item['total'],
                'limite': limite.faltas_maximas,
                'percentual': round(percentual),
                'critico': percentual >= 100,
            })

    return alertas


@login_required
def lista_faltas(request):
    faltas = faltas_permitidas_para_usuario(request.user)
    can_manage = can_manage_screen(request.user, Profile.SCREEN_FALTAS)

    return render(
        request,
        'faltas/lista.html',
        {
            'faltas': faltas,
            'can_manage': can_manage,
            'alertas_faltas': alertas_limite_faltas(faltas),
        }
    )


@manage_screen_required(Profile.SCREEN_FALTAS)
def criar_falta(request):
    form = FaltaForm(request.POST or None, user=request.user)

    if form.is_valid():
        form.save()
        return redirect('lista_faltas')

    return render(request, 'faltas/form.html', {'form': form, 'disciplinas_por_aluno': disciplinas_por_aluno_json(request.user)})


@manage_screen_required(Profile.SCREEN_FALTAS)
def editar_falta(request, id):
    falta = get_object_or_404(faltas_permitidas_para_usuario(request.user), id=id)
    form = FaltaForm(request.POST or None, instance=falta, user=request.user)

    if form.is_valid():
        form.save()
        return redirect('lista_faltas')

    return render(request, 'faltas/form.html', {'form': form, 'disciplinas_por_aluno': disciplinas_por_aluno_json(request.user)})


@manage_screen_required(Profile.SCREEN_FALTAS)
def excluir_falta(request, id):
    falta = get_object_or_404(faltas_permitidas_para_usuario(request.user), id=id)

    if request.method == 'POST':
        falta.delete()
        return redirect('lista_faltas')

    return render(request, 'faltas/confirmar_exclusao.html', {'falta': falta})


@manage_screen_required(Profile.SCREEN_FALTAS)
def registrar_chamada(request):
    form_data = request.POST if request.method == 'POST' else (request.GET or None)
    form = ChamadaForm(form_data, user=request.user)
    alunos = Aluno.objects.none()
    presencas_marcadas = set()

    if form.is_valid():
        disciplina = form.cleaned_data['disciplina']
        data = form.cleaned_data['data']
        alunos = filter_students_for_user(
            request.user,
            Aluno.objects.filter(disciplinas=disciplina).order_by('nome'),
        )

        chamada = Chamada.objects.filter(
            disciplina=disciplina,
            data=data,
        ).first()
        if chamada:
            presencas_marcadas = set(
                chamada.presencas.filter(presente=True).values_list('aluno_id', flat=True)
            )
        else:
            presencas_marcadas = set(alunos.values_list('id', flat=True))

        if request.method == 'POST':
            presentes_ids = {
                int(aluno_id)
                for aluno_id in request.POST.getlist('presentes')
                if aluno_id.isdigit()
            }

            with transaction.atomic():
                chamada, _ = Chamada.objects.update_or_create(
                    disciplina=disciplina,
                    data=data,
                    defaults={'professor': request.user},
                )

                for aluno in alunos:
                    presente = aluno.id in presentes_ids
                    PresencaChamada.objects.update_or_create(
                        chamada=chamada,
                        aluno=aluno,
                        defaults={'presente': presente},
                    )

                    if presente:
                        Falta.objects.filter(
                            aluno=aluno,
                            disciplina=disciplina,
                            data=data,
                        ).delete()
                    else:
                        Falta.objects.get_or_create(
                            aluno=aluno,
                            disciplina=disciplina,
                            data=data,
                            defaults={'justificada': False},
                        )

            messages.success(request, 'Chamada registrada com sucesso.')
            return redirect('lista_faltas')

    return render(
        request,
        'faltas/chamada.html',
        {
            'form': form,
            'alunos': alunos,
            'presencas_marcadas': presencas_marcadas,
        },
    )


@manage_screen_required(Profile.SCREEN_FALTAS)
def limites_faltas(request):
    form = LimiteFaltasForm(request.POST or None, user=request.user)

    if request.method == 'POST' and form.is_valid():
        LimiteFaltas.objects.update_or_create(
            disciplina=form.cleaned_data['disciplina'],
            defaults={
                'carga_horaria_total': form.cleaned_data['carga_horaria_total'],
                'percentual_maximo': form.cleaned_data['percentual_maximo'],
            },
        )
        messages.success(request, 'Limite de faltas salvo com sucesso.')
        return redirect('limites_faltas')

    return render(
        request,
        'faltas/limites.html',
        {
            'form': form,
            'limites': limites_permitidos_para_usuario(request.user),
        },
    )
