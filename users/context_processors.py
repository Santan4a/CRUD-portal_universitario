from .access import get_user_role, has_screen_access, is_aluno, is_gestao, is_professor
from .models import Profile


def access_flags(request):
    user = getattr(request, 'user', None)

    return {
        'user_role': get_user_role(user),
        'user_is_aluno': is_aluno(user),
        'user_is_gestao': is_gestao(user),
        'user_is_professor': is_professor(user),
        'can_access_gestao': has_screen_access(user, Profile.SCREEN_GESTAO),
        'can_access_alunos': has_screen_access(user, Profile.SCREEN_ALUNOS),
        'can_access_disciplinas': has_screen_access(user, Profile.SCREEN_DISCIPLINAS),
        'can_access_notas': has_screen_access(user, Profile.SCREEN_NOTAS),
        'can_access_faltas': has_screen_access(user, Profile.SCREEN_FALTAS),
    }
