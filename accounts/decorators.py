from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.is_superuser or request.user.role in roles:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, "Vous n'avez pas la permission d'accéder à cette page.")
            return redirect('dashboard')
        return wrapper
    return decorator