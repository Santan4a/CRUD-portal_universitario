from django.shortcuts import render

def contato(request):
    return render(request, 'contato.html')


def suporte(request):
    return render(request, 'suporte.html')


def politicas(request):
    return render(request, 'politicas.html')
