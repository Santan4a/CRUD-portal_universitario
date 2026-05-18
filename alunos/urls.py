from django.urls import path
from . import views

urlpatterns = [
    path('minha-area/', views.minha_area, name='minha_area'),
    path('', views.lista_alunos, name='lista_alunos'),

    path('novo/', views.criar_aluno, name='criar_aluno'),

    path(
        'editar/<int:id>/',
        views.editar_aluno,
        name='editar_aluno'
    ),

    path(
        'excluir/<int:id>/',
        views.excluir_aluno,
        name='excluir_aluno'
    ),

    path('dashboard/<int:id>/', views.dashboard_aluno, name='dashboard_aluno'),

    path(
    'tutor-ia-page/',
    views.pagina_tutor_ia,
    name='pagina_tutor_ia'
    ),

    path(
        'tutor-ia/',
        views.tutor_ia,
        name='tutor_ia'
    ),

]
