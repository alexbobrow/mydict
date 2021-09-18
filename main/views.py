from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max, Avg, Sum, Count, Prefetch, Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView

from .exceptions import NextWordNotFound
from .mixins import StaffMemberRequiredMixin
from .models import Word, Progress, Report


# similar to staff_member_required
# but returns 403 instead of redirect
from .tests.consts import ERROR_NO_WORDS


def staff_required_code(fn):
    def wrapped(*args, **kwargs):
        request = args[0]
        if not request.user.is_staff:
            return HttpResponseForbidden()
        return fn(*args, **kwargs)
    return wrapped


# similar to login_required
# but returns 403 instead of redirect
def login_required_code(fn):
    def wrapped(*args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        return fn(*args, **kwargs)
    return wrapped


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


def next(request):

    if request.user.is_authenticated:
        if 'progress_id' in request.POST:
            # fixating answer
            progress = Progress.objects.get(pk=request.POST['progress_id'])
            progress.add_answer(request.POST['answer_value'])

    filters = request.POST.get('filters', '')

    try:
        res, stata, debug = Progress.objects.get_next(request.user, filters)
    except NextWordNotFound:
        return JsonResponse({
            'error': ERROR_NO_WORDS
        })

    if request.user.is_authenticated:
        context = stata
        progress = res
        word = progress.word
        context['progressId'] = progress.id
        context['knowLast'] = progress.know_last
    else:
        context = {}
        progress = None
        word = res

    context['wordId'] = word.id
    context['en'] = word.word
    context['ru'] = word.translation
    context['pronounce'] = word.pronounce.url
    
    if request.user.is_staff:
        context['debug'] = debug

    return JsonResponse(context)


@login_required_code
def report_word(request):

    word = Word.objects.get(pk=request.POST['word_id'])

    report = Report.objects.create(
        user=request.user,
        word=word,
    )

    return JsonResponse({
        'success': True
    })


@staff_required_code
def delete_word(request):
    
    word = Word.objects.get(pk=request.POST['word_id'])
    word.disabled = True
    word.save()

    return JsonResponse({
        'success': True
    })


@staff_required_code
def admin_update_word(request):

    word = Word.objects.get(pk=request.POST['word_id'])
    word.old_translation = word.translation
    word.translation = request.POST['translation']
    word.save()

    return JsonResponse({
        'success': True
    })


@login_required_code
def user_prefs(request):
    name = request.POST['name']

    if name in ['show_sidebar', 'explicit', 'answer_delay']:
        value = bool(request.POST['value'])
    elif name in ['filters']:
        value = request.POST['value']
    else:
        raise Exception('Wrong params')

    setattr(request.user.preferences, name, value)

    request.user.preferences.save()

    return JsonResponse({
        'success': True
    })    
