from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from .models import Profile


DEFAULT_SCREENS_BY_ROLE = {
    Profile.ROLE_ALUNO: {
        Profile.SCREEN_DISCIPLINAS,
        Profile.SCREEN_NOTAS,
        Profile.SCREEN_FALTAS,
    },
    Profile.ROLE_PROFESSOR: {
        Profile.SCREEN_ALUNOS,
        Profile.SCREEN_NOTAS,
        Profile.SCREEN_FALTAS,
    },
    Profile.ROLE_GESTAO: {screen for screen, _ in Profile.SCREEN_CHOICES},
    'superuser': {screen for screen, _ in Profile.SCREEN_CHOICES},
}


def get_default_screens_for_role(role):
    default_screens = DEFAULT_SCREENS_BY_ROLE.get(role, set())

    return [
        screen
        for screen, _ in Profile.SCREEN_CHOICES
        if screen in default_screens
    ]


def get_user_role(user):
    if not user or not user.is_authenticated:
        return ''

    if user.is_superuser:
        return 'superuser'

    try:
        return user.profile.role
    except ObjectDoesNotExist:
        return ''


def get_allowed_screens(user):
    role = get_user_role(user)

    if role == 'superuser':
        return DEFAULT_SCREENS_BY_ROLE['superuser']

    try:
        profile = user.profile
    except (AttributeError, ObjectDoesNotExist):
        return set()

    if profile.allowed_screens is None:
        return DEFAULT_SCREENS_BY_ROLE.get(role, set())

    return set(profile.allowed_screens)


def has_screen_access(user, screen):
    if not user or not user.is_authenticated:
        return False

    return screen in get_allowed_screens(user)


def can_manage_screen(user, screen):
    return has_screen_access(user, screen) and not is_aluno(user)


def is_aluno(user):
    return get_user_role(user) == Profile.ROLE_ALUNO


def is_professor(user):
    return get_user_role(user) == Profile.ROLE_PROFESSOR


def is_gestao(user):
    return get_user_role(user) == Profile.ROLE_GESTAO


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if get_user_role(request.user) in roles:
                return view_func(request, *args, **kwargs)

            raise PermissionDenied

        return login_required(wrapper)

    return decorator


def screen_required(screen):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if has_screen_access(request.user, screen):
                return view_func(request, *args, **kwargs)

            raise PermissionDenied

        return login_required(wrapper)

    return decorator


def manage_screen_required(screen):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if can_manage_screen(request.user, screen):
                return view_func(request, *args, **kwargs)

            raise PermissionDenied

        return login_required(wrapper)

    return decorator
