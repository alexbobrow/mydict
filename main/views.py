
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.urls import reverse

from django.db.models import Max, Avg, Count, Prefetch

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Word, Progress, Report




# similar to staff_member_required
# but returns 403 instead of redirect
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
    return render(request, 'home.html', context)




def freq_next(request):

    word = Word.objects.get_next(request)
    context = {
        'wordId': word.id,
        'word': word.word,
        'translation': word.translation,
        'pronounce': word.pronounce.url,
        'added': False,
    }

    if request.user.is_authenticated:
        try:
            progress = Progress.objects.get(word=word, user=request.user, added=True)
            context['added'] = True
        except Progress.DoesNotExist:
            pass


    return JsonResponse(context)


@login_required_code
def own_next(request):
    try:
        progress = Progress.objects.get_next(request)
    except Progress.DoesNotExist:
        return JsonResponse({'error': 'Your dictionary is empty'})
    context = {
        'progressId': progress.id,
        'wordId': progress.word.id,
        'word': progress.word.word,
        'translation': progress.word.translation,
        'pronounce': progress.word.pronounce.url,
        'added': progress.added,
    }
    return JsonResponse(context)




@login_required
def freq_list(request):
    context = {}

    pqs = Progress.objects.filter(user=request.user, added=True)
    qs = Word.objects.filter(disabled=False).prefetch_related(Prefetch('progress_set', queryset=pqs))


    paginator = Paginator(qs, 100)

    page = request.GET.get('page', 1)
    try:
        words = paginator.page(page)
    except PageNotAnInteger:
        return redirect(reverse('freq_list'))
    except EmptyPage:
        url = "%s?page=%s" % (reverse('freq_list'), paginator.num_pages)
        return redirect(url)

    context['words'] = words
    context['type'] = 'freq'

    return render(request, 'freq_list.html', context)




@login_required
def own_list(request):
    context = {}

    context = {}

    qs = Progress.objects.filter(user=request.user, added=True, word__disabled=False).select_related('word')
    paginator = Paginator(qs, 1000)

    page = request.GET.get('page', 1)
    try:
        words = paginator.page(page)
    except PageNotAnInteger:
        return redirect(reverse('freq_list'))
    except EmptyPage:
        url = "%s?page=%s" % (reverse('freq_list'), paginator.num_pages)
        return redirect(url)

    context['words'] = words
    context['type'] = 'own'

    return render(request, 'own_list.html', context)



def freq_cards(request):
    context = {}
    context['type'] = 'freq'
    return render(request, 'cards.html', context)


@login_required
def own_cards(request):
    context = {}
    context['type'] = 'own'
    return render(request, 'cards.html', context)









def login_view(request):

    context = {}

    next_url = request.GET.get('next', '/')

    if request.user.is_authenticated():
        return redirect(next_url)


    if 'login' in request.POST:

        user = authenticate(
            username=request.POST['login'],
            password=request.POST['password']
        )
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(next_url)
            else:
                messages.error(request, 'Account is disabled')
        else:
            messages.error(request, 'Wrong login or password')
    

    return render(request, 'login.html', context)




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
def update_word(request):

    word = Word.objects.get(pk=request.POST['word_id'])
    word.old_translation = word.translation
    word.translation = request.POST['translation']
    word.save()

    return JsonResponse({
        'success': True
    })




@login_required_code
def add_word(request):

    word = Word.objects.get(pk=request.POST['word_id'])

    progress, created = Progress.objects.get_or_create(
        word=word,
        user=request.user,
    )

    progress.added = True
    progress.save()
    
    """    
    user_word = models.CharField(max_length=255)
    user_translation = models.CharField(max_length=255)
    user_comment = models.CharField(max_length=255)
    """

    return JsonResponse({
        'success': True
    })



@login_required_code
def remove_word(request):

    word = Word.objects.get(pk=request.POST['word_id'])

    progress = Progress.objects.get(word=word, user=request.user)
    progress.added = False
    progress.save()

    return JsonResponse({
        'success': True
    })