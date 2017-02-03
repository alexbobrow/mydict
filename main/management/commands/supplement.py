from django.core.management.base import BaseCommand, CommandError
from main.models import Translation, Pronounce, WordOs, WordWf
#from django.contrib.auth.models import User



class Command(BaseCommand):
    
    help = 'Check and and new words to Pronounce and Translate from Words Os and Wf'

    def handle(self, *args, **options):

        


        self.stdout.write('Adding to Translation from Os')

        words = WordOs.objects.all()

        added = 0;
        x = 0;
        l = len(words)
        for word in words:

            x += 1
            if x % 100 == 0:
                self.stdout.write('%s/%s' % (x,l))


            translation, created = Translation.objects.get_or_create(
                word=word.word,
                defaults={'base': False}
            )

            if created:
                added += 1

        self.stdout.write('Added %s:' % added)

        



        self.stdout.write('Adding to Pronounce from Os')

        words = WordOs.objects.all()

        added = 0;
        x = 0;
        l = len(words)
        for word in words:

            x += 1
            if x % 100 == 0:
                self.stdout.write('%s/%s' % (x,l))


            promounce, created = Pronounce.objects.get_or_create(
                word=word.word
            )

            if created:
                added += 1

        self.stdout.write('Added %s:' % added)




        self.stdout.write('Adding to Translation from Wf')

        words = WordWf.objects.all()

        added = 0;
        x = 0;
        l = len(words)
        for word in words:

            x += 1
            if x % 100 == 0:
                self.stdout.write('%s/%s' % (x,l))



            translation, created = Translation.objects.get_or_create(
                word=word.word,
                defaults={'base': False}
            )

            if created:
                added += 1

        self.stdout.write('Added %s:' % added)

        



        self.stdout.write('Adding to Pronounce from Wf')

        words = WordWf.objects.all()

        added = 0;
        x = 0;
        l = len(words)
        for word in words:

            x += 1
            if x % 100 == 0:
                self.stdout.write('%s/%s' % (x,l))


            promounce, created = Pronounce.objects.get_or_create(
                word=word.word
            )

            if created:
                added += 1

        self.stdout.write('Added %s:' % added)