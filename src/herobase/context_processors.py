from herobase.forms import UserAuthenticationForm

def auth(request):
    if (request.user.is_anonymous()):
        return {'login_form': UserAuthenticationForm}
    return {}