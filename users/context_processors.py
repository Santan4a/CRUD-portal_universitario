from .access import get_user_role, is_aluno, is_gestao, is_professor


def access_flags(request):
    user = getattr(request, 'user', None)

    return {
        'user_role': get_user_role(user),
        'user_is_aluno': is_aluno(user),
        'user_is_gestao': is_gestao(user),
        'user_is_professor': is_professor(user),
    }
