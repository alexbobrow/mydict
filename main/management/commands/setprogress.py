import random

from django.core.management.base import BaseCommand, CommandError
from main.models import Progress, Word
from django.contrib.auth.models import User

class Command(BaseCommand):
    
    help = 'Adding words to user progress'

    def handle(self, *args, **options):


        uid = input('Enter user id: ')
        user = User.objects.get(id=uid)

        self.stdout.write('User %s selected: ' % user)

        total = int(input('Enter total words in user progress list: '))

        current_count = user.progress_set.count()

        need_to_add = int(total) - current_count


        self.stdout.write('User has %s word(s), need to add %s' % (current_count, need_to_add))


        if need_to_add<=0:
            self.stdout.write('Cancelation. User already has %s word(s)' % (current_count))
            return

        self.stdout.write('Adding new words...')

        exclude = Progress.objects.filter(user=user).values('word_id')
        words = Word.objects.filter(disabled=False).exclude(id__in=exclude)

        self.stdout.write('Source count %s' % words.count())

        words = list(words)
        for x in range(0, need_to_add):
            try:
                word = words[x]
            except:
                self.stdout.write('Exception on x %s' % x)
                raise


            progress = Progress.objects.create(
                user=user,
                word=word,
                showed=1
            )        
