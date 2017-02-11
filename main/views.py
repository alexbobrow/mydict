

from django.http import JsonResponse
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages



from .models import Word, Progress, ProgressLog, Report



@login_required
def root(request):
    
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

    progress = Progress.objects.get(pk=request.POST['progress_id'])

    if request.POST['answer_id']=='0':
        # skip mode (plain enter on empty field)
        answer = None 
    else:
        answer = Word.objects.get(pk=request.POST['answer_id'])

    if progress.word==answer:

        if progress.asked == 0:
            # first answer and it is right
            # treat like 3 right answers
            progress.asked=3
            progress.correct_answers=3
        elif progress.asked==3 and progress.correct_answers==3:
            # second right answer in a row
            # treat like 2 right answers
            progress.asked=5
            progress.correct_answers=5
        else:
            # for other right answers adding 1
            progress.correct_answers = progress.correct_answers + 1
            progress.asked = progress.asked + 1
        correct = True 

    else:
        correct = False
        progress.asked = progress.asked + 1
    
    # ratio filed updated in save() method
    progress.save()


    # mark in log that word is answered (no matter correct or not)
    progress_log = ProgressLog.objects.get(progress=progress)
    progress_log.answered = True
    progress_log.save()
    #ProgressLog.objects.mark_answered(progress)
  

    return JsonResponse({
        'correct': correct,
        'correctTranslation': progress.word.translation,
        'answerWord': answer.word,
        'answerTranslation': answer.translation,
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





@login_required
def report_word(request):

    progress = Progress.objects.get(pk=request.POST['progress_id'])

    report = Report.objects.create(
        user=request.user,
        word=progress.word,
        text=request.POST['message'],
    )

    return JsonResponse({
        'success': True
    })