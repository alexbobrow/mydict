from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Max, Avg, Sum, Count, Prefetch, Q
from django.views.generic import ListView

from .mixins import StaffMemberRequiredMixin
from .models import Word, Progress


class WordsListView(LoginRequiredMixin, ListView):

    template_name = 'list.html'
    paginate_by = 100
    page_kwarg = 'p'
    raise_exception = True

    def get_queryset(self):
        qs = Word.objects.filter(disabled=False)

        if self.request.GET.get('q'):
            qs = qs.filter(Q(word__icontains=self.request.GET['q']) | Q(translation__icontains=self.request.GET['q']))

        pqs = Progress.objects.filter(user=self.request.user)
        qs = qs.prefetch_related(Prefetch('progress_set', queryset=pqs))
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super(WordsListView, self).get_context_data()
        context['q'] = self.request.GET.get('q')
        return context


class StataView(StaffMemberRequiredMixin, ListView):

    template_name = 'stata.html'
    raise_exception = True

    def get_queryset(self):
        users = User.objects.all().annotate(
            last_activity=Max('progress__time_updated'),
            dict_size=Count('progress'),
            know_last=Avg('progress__know_last'),
            know_count=Sum('progress__know_count'),
        )
        return users
