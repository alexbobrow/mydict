import time
import requests

from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from main.models import Word, WordOs, WordWf, Pronounce, Translation

class Command(BaseCommand):
    
    help = 'Combine source tables, translation and pronounce into one table'

   
    def handle(self, *args, **options):

        # loop over first, add translation and pronounce
        # correct freq relative to variable
        # skip if no translation or pronounce

        # loop over the second, add if not exist, add translation and pronounce
        # skip if no translation or pronounce       
        # correct freq relative to variable

        self.process(WordOs, 1)

        self.process(WordWf, 0.28)




    def process(self, sourceTable, mult):

        total = sourceTable.objects.count()
        words = sourceTable.objects.all()
            

        skipped = 0;
        
        self.stdout.write('Processing %s...' % sourceTable)

        for i, word in enumerate(words):

            try:
                w = Word.objects.get(word=word.word)
                skipped += 1
                continue
            except Word.DoesNotExist:
                pass


            self.stdout.write('\r%s/%s, skipped: %s' % (i, total, skipped), ending='')
            self.stdout.flush()

            try:
                p = Pronounce.objects.get(word=word.word, status=True)
            except Pronounce.DoesNotExist:
                skipped += 1
                continue

            if p.file == '':
                skipped += 1
                continue

            try:
                t = Translation.objects.get(word=word.word, status=True)
            except Translation.DoesNotExist:
                skipped += 1
                continue

            if t.translation == '':
                skipped += 1
                continue

            frequency = int(word.frequency * mult)

            new_word = Word.objects.create(
                word=word.word,
                translation=t.translation,
                base=t.base,
                frequency=frequency,
                rank=0,
                pronounce=p.file,
            )


        self.stdout.write('\n')
        self.stdout.write(self.style.SUCCESS('Everything is done!'))
