from django.conf import settings
from django.contrib.auth.decorators import user_passes_test


def anonymous_required(function=None, redirect_url=None):
    '''
    Decorator for views that checks that the user isn't logged,
    redirects to the home page if necessary.
    '''
    if not redirect_url:
        redirect_url = settings.LOGIN_REDIRECT_URL

    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous,
        login_url=redirect_url
    )

    if function:
        return actual_decorator(function)
    return actual_decorator
