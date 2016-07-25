from django.core.management.base import BaseCommand, CommandError
from main.models import Word, WordManager

class Command(BaseCommand):
    
    help = 'Testing WordManager._getRange'



    
    def handle(self, *args, **options):


        # count of user words to test
        words = 1000

        results = {}

        for x in range(0,5000):
            res =  Word.objects._getRange(words)
            key = str(res[0]) + '_' + str(res[1])

            if not key in results:
                results[key] = 0

            results[key] += 1


        total = 0
        for key, value in results.iteritems():
            total += value

        for key, value in results.iteritems():
            percent = value * 100 / total
            print "%s -> %s [%s%%]" % (key, value, percent)