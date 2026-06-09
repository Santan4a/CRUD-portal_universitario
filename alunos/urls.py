from django.urls import path
from . import views

urlpatterns = [
    path('minha-area/', views.minha_area, name='minha_area'),

    path(
        'minha-area/exportar-notas/',
        views.exportar_notas_aluno,
        name='exportar_notas_aluno'
    ),

    path('', views.lista_alunos, name='lista_alunos'),

    path('dashboard/<int:id>/', views.dashboard_aluno, name='dashboard_aluno'),

    path('tutor-ia-page/', views.pagina_tutor_ia, name='pagina_tutor_ia'),

    path('tutor-ia/', views.tutor_ia, name='tutor_ia'),
]