

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.db.models import Max, Avg, Count


from .models import Word, Progress, Report



def root(request):
 
    context = {}

    return render(request, 'app.html', context)



@login_required
def next(request):

    rand, word = Word.objects.get_next()

    context = {
        'id': word.id,
        'rand': rand,
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




@staff_member_required
def disable_word(request):
    progress = Progress.objects.get(pk=request.POST['progress_id'])
    progress.word.disabled = True
    progress.word.save()

    qs = Progress.objects.filter(word=progress.word)
    qs.delete()

    return JsonResponse({
        'success': True
    })





@login_required
def report_word(request):

    if 'progress_id' in request.POST:
        progress = Progress.objects.get(pk=request.POST['progress_id'])
        word = progress.word
    else:
        word = Word.objects.get(pk=request.POST['word_id'])

    report = Report.objects.create(
        user=request.user,
        word=word,
        text=request.POST['message'],
    )

    return JsonResponse({
        'success': True
    })

