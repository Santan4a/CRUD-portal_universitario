from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_disciplinas, name='lista_disciplinas'),
    path('criar/', views.criar_disciplina, name='criar_disciplina'),
    path('editar/<int:id>/', views.editar_disciplina, name='editar_disciplina'),
    path('excluir/<int:id>/', views.excluir_disciplina, name='excluir_disciplina'),
]