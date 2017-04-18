from main.models import Preferences

class SimpleMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response



    def __call__(self, request):

        if request.user.is_authenticated:
            try:
                request.user.preferences
            except Preferences.DoesNotExist:
                p = Preferences.objects.create(user=request.user, filters='0')

        response = self.get_response(request)

        return response