import time
import requests

from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from main.models import Word

class Command(BaseCommand):
    
    help = 'Grab word pronounciation from gstatic server'

    #def add_arguments(self, parser):
    #    parser.add_argument('poll_id', nargs='+', type=int)
    
    def handle(self, *args, **options):

        total = Word.objects.count()
        words = Word.objects.filter(gstatic=None).order_by('rank').all()[0:2000]
        
        found = 0
        notfound = 0

        self.stdout.write('Processing pronounciation grabs...')

        last = len(words)-1

        for i, word in enumerate(words):

            e = '\n' if i==last else ''

            self.stdout.write('\rword %s/%s, found: %s, not found: %s' % (word.rank, total, found, notfound), ending=e)
            self.stdout.flush()

            request = requests.get('http://gstatic.com/dictionary/static/sounds/de/0/%s.mp3' % word.word)

            if request.status_code==200:
                found += 1
                word.pronounce.save('%s.mp3' % word.word, ContentFile(request.content))
                word.gstatic = True
                word.save()
            else:
                word.gstatic = False
                word.save()
                notfound += 1

            time.sleep(0.5)


        self.stdout.write(self.style.SUCCESS('Everything is done!'))