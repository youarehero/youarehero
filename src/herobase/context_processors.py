from herobase.forms import UserAuthenticationForm
from herobase.models import Quest

def login_form(request):
    """Add login_form to template context if the user is not authenticated."""
    if request.user.is_anonymous():
        return {'login_form': UserAuthenticationForm}
    return {}
