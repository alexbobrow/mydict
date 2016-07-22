

from django.http import JsonResponse
from django.shortcuts import render




from .models import Word




def root(request):

    


    context = {}
    return render(request, 'app.html', context)


def next(request):

    word = Word.objects.getNext(request.user)

    return JsonResponse({
        'word': word.word,
        'translation': word.translation,
    })

    


def autocomplete(request):
    pass


