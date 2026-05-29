from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_notas, name='lista_notas'),
    path('nova/', views.criar_nota, name='criar_nota'),
    path('editar/<int:id>/', views.editar_nota, name='editar_nota'),
    path('deletar/<int:id>/', views.deletar_nota, name='deletar_nota'),
    path(
    'exportar/',
    views.exportar_notas,
    name='exportar_notas'
),

path(
    'exportar/pdf/',
    views.exportar_pdf,
    name='exportar_pdf'
),

path(
    'exportar/excel/',
    views.exportar_excel,
    name='exportar_excel'
),
]