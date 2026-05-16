from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .access import get_user_role


@login_required
def portal_redirect(request):
    role = get_user_role(request.user)

    if role == 'aluno':
        return redirect('minha_area')

    if role == 'gestao':
        return redirect('dashboard_gestao')

    if role == 'professor':
        return redirect('lista_alunos')

    return redirect('login')


@login_required
def dashboard_gestao(request):
    role = get_user_role(request.user)

    if role != "gestao":
        return redirect("home")

    return render(request, "gestao/dashboard.html")

from django.shortcuts import render

def contato(request):
    return render(request, 'contato.html')

def suporte(request):
    return render(request, 'suporte.html')

def politicas(request):
    return render(request, 'politicas.html')