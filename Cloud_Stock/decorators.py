from django.shortcuts import redirect


def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if "username" not in request.session:
            return redirect("login")
        return view_func(request, *args, **kwargs)

    return wrapper
