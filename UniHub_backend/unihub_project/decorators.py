from functools import wraps
from django.shortcuts import redirect

def verification_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if getattr(request.user, 'email_verified', False):
            return view_func(request, *args, **kwargs)
        return redirect('Verify_page')
    return _wrapped_view
