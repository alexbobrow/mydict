from django.contrib.auth.mixins import AccessMixin

from main.models import Preferences


class StaffMemberRequiredMixin(AccessMixin):
    """Verify that the current user is staff member."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_active or not request.user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class AppContextMixin:

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.request.user.is_authenticated:
            context['user_prefs'], _ = Preferences.objects.get_or_create(user=self.request.user)
        else:
            context['user_prefs'] = dict(
                show_sidebar=True,
                filters='0',
                answer_delay=False,
            )
        return context
