from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_disciplinas, name='lista_disciplinas'),
]