from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_administrator():
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

def finance_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_finance():
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

def normal_user_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_normal_user():
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view