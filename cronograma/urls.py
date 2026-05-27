from django.urls import path

from .views import grade_horarios

urlpatterns = [

    path(
        'grade/',
        grade_horarios,
        name='grade_horarios'
    ),
]