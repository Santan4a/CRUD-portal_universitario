from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied


def get_user_role(user):
    if not user or not user.is_authenticated:
        return ''

    if user.is_superuser:
        return 'superuser'

    try:
        return user.profile.role
    except ObjectDoesNotExist:
        return ''


def is_aluno(user):
    return get_user_role(user) == 'aluno'


def is_professor(user):
    return get_user_role(user) == 'professor'


def is_gestao(user):
    return get_user_role(user) == 'gestao'


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if get_user_role(request.user) in roles:
                return view_func(request, *args, **kwargs)

            raise PermissionDenied

        return login_required(wrapper)

    return decorator
