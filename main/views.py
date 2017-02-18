

from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.db.models import Max, Avg, Count


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
    return render(request, 'app.html', context)




def next(request):
    word = Word.objects.get_next(request)
    context = {
        'id': word.id,
        'word': word.word,
        'translation': word.translation,
        'pronounce': word.pronounce.url,
    }
    return JsonResponse(context)




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
def skip_word(request):
    progress = Progress.objects.get(word__id=request.POST['word_id'])
    progress.skip = True
    progress.save()

    return JsonResponse({
        'success': True
    })




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
