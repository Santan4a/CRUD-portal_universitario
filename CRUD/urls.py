from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from users import views
from users.views import portal_redirect


urlpatterns = [
    path(
        '',
        LoginView.as_view(
            template_name='registration/login.html',
            redirect_authenticated_user=True,
        ),
        name='home'
    ),
    path(
        'login/',
        LoginView.as_view(
            template_name='registration/login.html',
            redirect_authenticated_user=True,
        ),
        name='login'
    ),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('portal/', portal_redirect, name='portal'),
    path('admin/', admin.site.urls),

    path('alunos/', include('alunos.urls')),
    path('disciplinas/', include('disciplinas.urls')),
    path('faltas/', include('faltas.urls')),
    path('notas/', include('notas.urls')),

    
    path('contato/', views.contato, name='contato'),
    path('suporte/', views.suporte, name='suporte'),
    path('politicas/', views.politicas, name='politicas'),

    
    path(
        "gestao/dashboard/",
        views.dashboard_gestao,
        name="dashboard_gestao"
    ),
    path(
        "gestao/usuarios/novo/",
        views.cadastrar_aluno_gestao,
        name="cadastrar_usuario_gestao"
    ),
    path(
        "gestao/alunos/novo/",
        views.cadastrar_aluno_gestao,
        name="cadastrar_aluno_gestao"
    ),
    path(
        "gestao/alunos/<int:id>/editar/",
        views.editar_aluno_gestao,
        name="editar_aluno_gestao"
    ),

    path(
    "gestao/alunos/<int:id>/excluir/",
    views.excluir_aluno_gestao,
    name="excluir_aluno_gestao"
    
    ),

]
