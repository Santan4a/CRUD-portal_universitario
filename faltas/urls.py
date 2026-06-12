from django.urls import path

from . import views


urlpatterns = [
    path('', views.lista_faltas, name='lista_faltas'),
    path('nova/', views.criar_falta, name='criar_falta'),
    path('chamada/', views.registrar_chamada, name='registrar_chamada'),
    path('limites/', views.limites_faltas, name='limites_faltas'),
    path('editar/<int:id>/', views.editar_falta, name='editar_falta'),
    path('excluir/<int:id>/', views.excluir_falta, name='excluir_falta'),
]
