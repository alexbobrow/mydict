

from django.http import JsonResponse
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages



from .models import Word, Progress



@login_required
def root(request):


    context = {}
    return render(request, 'app.html', context)



@login_required
def next(request):

    progress = Progress.objects.getNext(request.user)

    context = {
        'word': progress.word.word,
        'id': progress.pk,
    }

    if request.user.is_staff:
        context['debug'] = [{'key':k, 'value':v} for k, v in progress.debug.iteritems()]

    return JsonResponse(context)




@login_required
def answer(request):

    progress = Progress.objects.get(pk=request.POST['progress_id'])
    answer = Word.objects.get(pk=request.POST['answer_id'])

    if progress.word==answer:
        progress.correct_answers = progress.correct_answers + 1
        correct = True 
    else:
        correct = False

    progress.asked = progress.asked + 1
    # ratio filed updated in save() method
    progress.save()
   

    return JsonResponse({
        'correct': correct,
        'answer': progress.word.translation,
    })









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


    

@login_required
def suggest(request):
    qs = Word.objects.getSuggest(request.GET['value'])
    context = {
        'items': qs
    }
    return render(request, 'suggest.html', context)





@staff_member_required
def disable_word(request):
    progress = Progress.objects.get(pk=request.POST['progress_id'])
    progress.word.disabled = True
    progress.word.save()

    qs = Progress.objects.get(word=progress.word)
    qs.delete()

    return JsonResponse({
        'success': True
    })