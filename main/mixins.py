from django.contrib.auth.mixins import AccessMixin


class StaffMemberRequiredMixin(AccessMixin):
    """Verify that the current user is staff member."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_active or not request.user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
