from django.core.management.base import BaseCommand, CommandError
from main.models import Word, Progress, ProgressLog
from django.contrib.auth.models import User

class Command(BaseCommand):
    
    help = 'Adding words to user progress list and set ratio on them'

    def handle(self, *args, **options):

        uid = input('Enter user id: ')
        
        user = User.objects.get(id=uid)

        self.stdout.write('User %s selected: ' % user)

        wid = input('Enter word id: ')

        word = Word.objects.get(id=wid)

        self.stdout.write('Word %s selected: ' % word)

        # get progress object
        try:
            progress = Progress.objects.get(word=word, user=user)
            self.stdout.write('Exist %s' % progress.id )
        except Progress.DoesNotExist:
            progress = Progress.objects.create(word=word, user=user)
            self.stdout.write('Does not exist, creating...')

        # set all entries in user log as answered
        log_words = ProgressLog.objects.filter(progress__user=user)
        log_words.update(answered=True)

        # add new word in progress
        ProgressLog.objects.add(progress)

        self.stdout.write(self.style.SUCCESS('Done!'))





