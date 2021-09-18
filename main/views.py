from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max, Avg, Sum, Count, Prefetch, Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse

from .exceptions import NextWordNotFound
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


def root(request):
    context = {}
    return render(request, 'about.html', context)


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
def list(request):
    context = {}

    qs = Word.objects.filter(disabled=False)

    if 'q' in request.GET and request.GET['q']:
        qs = qs.filter(Q(word__icontains=request.GET['q']) | Q(translation__icontains=request.GET['q'])) 
        context['q'] = request.GET['q']

    pqs = Progress.objects.filter(user=request.user)
    qs = qs.prefetch_related(Prefetch('progress_set', queryset=pqs))

    paginator = Paginator(qs, 100)

    page = request.GET.get('p', 1)
    try:
        words = paginator.page(page)
    except PageNotAnInteger:
        return redirect(reverse('list'))
    except EmptyPage:
        url = "%s?page=%s" % (reverse('list'), paginator.num_pages)
        return redirect(url)

    context['words'] = words

    return render(request, 'list.html', context)


def cards(request):
    context = {}
    return render(request, 'cards.html', context)


def logout_view(request):
    next_url = request.GET.get('next', '/')
    logout(request)
    return redirect(next_url)


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


@staff_member_required
def stata(request):
    users = User.objects.all().annotate(
        last_activity=Max('progress__time_updated'),
        dict_size=Count('progress'),
        know_last=Avg('progress__know_last'),
        know_count=Sum('progress__know_count'),
    )
    return render(request, 'stata.html', {'users': users})


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
