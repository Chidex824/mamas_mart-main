from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from accounts.models import Role

ROLE_PERMISSIONS = {
    Role.ADMIN: [
        'can_view_dashboard',
        'can_manage_inventory',
        'can_manage_sales',
        'can_manage_purchases',
        'can_manage_users',
        'can_view_reports',
        'can_process_sales',
    ],
    Role.MANAGER: [
        'can_view_dashboard',
        'can_manage_inventory',
        'can_manage_sales',
        'can_manage_purchases',
        'can_view_reports',
        'can_process_sales',
    ],
    Role.STAFF: [
        'can_view_dashboard',
        'can_manage_inventory',
        'can_process_sales',
        'can_view_reports',
    ],
    Role.CASHIER: [
        'can_view_dashboard',
        'can_process_sales',
    ],
}

# Optional alias using string keys
ROLE_PERMISSIONS_BY_NAME = {
    'admin': ROLE_PERMISSIONS[Role.ADMIN],
    'manager': ROLE_PERMISSIONS[Role.MANAGER],
    'staff': ROLE_PERMISSIONS[Role.STAFF],
    'cashier': ROLE_PERMISSIONS[Role.CASHIER],
}


def role_required(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_superuser or (
                request.user.role and request.user.role.name in allowed_roles
            ):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied

        return _wrapped_view

    return decorator


def permission_required(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_superuser or request.user.has_perm(f'accounts.{permission_name}'):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied

        return _wrapped_view

    return decorator
