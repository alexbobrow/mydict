from django.core.management.base import BaseCommand, CommandError
from main.models import Word

class Command(BaseCommand):
    
    help = 'Refresh rank value according to frequency field'

    #def add_arguments(self, parser):
    #    parser.add_argument('poll_id', nargs='+', type=int)
    
    def handle(self, *args, **options):

        total = Word.objects.count()
        words = Word.objects.order_by('-frequency').all()
        i = 1

        for word in words:

            r = '' if i==1 else '\r'
            e = '\n' if i==total else ''

            self.stdout.write('%sProcessing %s/%s' % (r, i, total), ending=e)
            self.stdout.flush()

            word.rank = i
            word.save()
            i+=1

        self.stdout.write(self.style.SUCCESS('Everything is done!'))


