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

    

]
