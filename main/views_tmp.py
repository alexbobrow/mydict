import os
import urllib
from datetime import timedelta

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone



from .models import Word, WordWf, Translation

# TEMP


def next_for_translate(request):

    try:
        word = Translation.objects.filter(status=None).first()
        result = {
            'ok': True,
            'word': word.word,
            'id': word.id,
        }

    except Translation.DoesNotExist:
        result = {
            'ok': False,
            'error': 'No words for translation',
        }

    response = JsonResponse(result)
    response['Access-Control-Allow-Origin'] = '*'

    return response




@csrf_exempt
def import2(request):
    """
    For import 5000 words from http://www.wordfrequency.info/
    """

    word = WordSecond()
    try:
        word.word = request.POST['word']
        word.frequency = request.POST['frequency']
        word.save()
        result = {
            'ok': True,
        }
    except Exception as e:
        from pprint import pprint;
        result = {
            'ok': False,
            'error': '%s: %s' % (type(e), e.message),
        }


    response = JsonResponse(result)
    response['Access-Control-Allow-Origin'] = '*'

    return response






def add_import(request):

    words2 = WordSecond.objects.all()

    for word2 in words2:

        try:
            word1 = Word.objects.get(word=word2.word)
            word1.frequency2 = word2.frequency
            word1.save()
        except Word.DoesNotExist:
            word1 = Word()
            word1.word = word2.word
            word1.frequency2 = word2.frequency
            word1.frequency = int(word2.frequency / 3.5)
            word1.save()


    return HttpResponse('DONE NAKONETS TO')






def list(request):

    #words = Word.objects.all()[0:1000]
    words = Word.objects.all()
    #words = Word.objects.filter(word__iendswith='s')

    context = {
        'words': words
    }
    

    return render(request, 'tmplist.html', context)




def control(request):

    time_threshold = timezone.now() - timedelta(minutes=3)
    last = Translation.objects.exclude(time_updated__lt=time_threshold).count()
    if (last<1):
    #if (True):

        url = 'https://api.telegram.org/bot170568722:AAEdXnlzY3-0JPFlgo8Hh73DonSYSzo5lLY/sendMessage'
        values = dict(text='Translation stopped working...', chat_id=122775874)

        """
        python2
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        rsp = urllib2.urlopen(req)
        content = rsp.read()
        """

        #python3

        import urllib.request
        import urllib.parse
        data = urllib.parse.urlencode(values)
        rsp = urllib.request.urlopen(url, data)
        content = rsp.read()

        #raise Exception("CARAUL!!!")


    left = Translation.objects.filter(status=None).count()
    

    context = {
        'left': left
    }
    

    return render(request, 'tmpcontrol.html', context)    


def combine(request):

    if (request.POST['src'] == request.POST['dst']):
        return JsonResponse({'ok': False, 'error':'With itself'})        
   
    wordSrc = Word.objects.get(id=request.POST['src'])
    wordDst = Word.objects.get(id=request.POST['dst'])

    wordDst.frequency = wordDst.frequency + wordSrc.frequency
    wordDst.save()

    wordSrc.delete()

    return JsonResponse({'ok': True})



def delete(request):

    word = Word.objects.get(id=request.POST['id'])
    word.delete()

    return JsonResponse({'ok': True})



def rename(request):

    word = Word.objects.get(id=request.POST['id'])
    word.word = request.POST['edited']
    word.save()

    return JsonResponse({'ok': True})



def autocomplete(request):

    qs = Word.objects.filter(word__istartswith=request.GET['value']).exclude(id=request.GET['exclude'])[:20]
   
    context = {
        'words': qs
    }

    return render(request, 'tmpsuggest.html', context)




@csrf_exempt
def save_translation(request):
    # word[]
    # base | boolean
    # word_id

    words = request.POST.getlist('word')
    word = Translation.objects.get(id=request.POST['word_id'])

    try:
        word.translation = ", ".join(words)
        word.status = True
        word.base = request.POST['base']
        word.save()
        ans = {'ok': True}
    except Exception as e:
        ans = {'ok': False, 'error': 'Save:%s' % e.message }

    
    response = JsonResponse(ans)
    response['Access-Control-Allow-Origin'] = 'https://translate.google.com'
    return response




def create_from_txt(request):

    dictname = os.path.join(settings.BASE_DIR, 'en.txt')

    res = ''
    
    with open(dictname) as file:
        lines = [line.rstrip('\n') for line in file]


        for line in lines[:15000]:
            parts = line.split(' ')
            if len(parts)!=2:
                raise Exception('PPC, TRI CHASTI ((')

            res = res + parts[0] + '<br>' 

            Word.objects.create(word=parts[0], frequency=parts[1])


    return HttpResponse(res)
