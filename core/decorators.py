from django.core.exceptions import PermissionDenied
from .models import CreatorProfile

def is_active(function):
    def wrap(request, *args, **kwargs):
        creator_profile = CreatorProfile.objects.get(user=request.user)

        if creator_profile.is_active:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap