

from django.http import JsonResponse
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages



from .models import Word, Progress, ProgressLog, Report



def root(request):

    # internal redirect to login
    if not request.user.is_authenticated:
        return login_view(request)
    

    context = {}

    if request.user.has_perm('main.tester'):
        context['tester'] = True
    else:
        context['tester'] = False

    return render(request, 'app.html', context)



@login_required
def next(request):

    progress = Progress.objects.getNext(request.user)

    
    # last 10 words we keep in session
    # TODO may be store'em in DB
    """
    if 'log' in request.session:
        log = request.session['log']
        if len(log)>=10:
            log = log[1:]
    else:
        log = []  
    log.append(progress.pk)
    request.session['log'] = log
    progress.debug.append({'key': 'log','value': log})
    """


    context = {
        'word': progress.word.word,
        'id': progress.pk,
        'pronounce': progress.word.pronounce.url,
    }

    if request.user.has_perm('main.tester'):
        context['debug'] = progress.debug

    return JsonResponse(context)



@login_required
def answer(request):

    progress = Progress.objects.get(pk=request.POST['progress_id'], user=request.user)

    if 'answer_id' in request.POST:
        # answer selected via autocomplete
        #answer = Word.objects.get(pk=request.POST['answer_id'], disabled=False)
        success, user_word = progress.apply_answer(id=request.POST['answer_id'])
    else:
        # answer typed manually
        # if not match answer is None
        #answer = progress.check_text_answer(request.POST['answer_text'])
        success, user_word = progress.apply_answer(text=request.POST['answer_text'])

    #correct, exact = progress.apply_answer(answer)

    resp = {
        'success': success,
        'correctWord': {
            'translation': progress.word.translation,
        }
    }

    # adding reverse translation of user selected answer
    if user_word:
        resp.update({
            'userWord': {
                'id': user_word.pk,
                'word': user_word.word,
                'translation': user_word.translation,
                'pronounce': user_word.pronounce,
            }
        })

    return JsonResponse(resp)








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