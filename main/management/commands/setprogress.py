import random

from django.core.management.base import BaseCommand, CommandError
from main.models import Progress
from django.contrib.auth.models import User

class Command(BaseCommand):
    
    help = 'Adding words to user progress list and set ratio on them'

    def handle(self, *args, **options):


        uid = input('Enter user id: ')
        user = User.objects.get(id=uid)

        self.stdout.write('User %s selected: ' % user)

        total = int(input('Enter total words in user progress list: '))

        asked = int(input('Enter avarage asked: '))

        rating = float(input('Enter avarage rating: '))
        rating100 = int(round(rating*100))


        current_count = user.progress_set.count()

        need_to_add = int(total) - current_count


        self.stdout.write('User has %s word(s), need to add %s' % (current_count, need_to_add))

        self.stdout.write('Updating rating for old words...')


        for progress in user.progress_set.all():
            # asked
            a = random.randint(asked-2, asked+2)
            # ratio
            r = random.randint(rating100-20, rating100+20)
            # correct
            #import pdb; pdb.set_trace()
            c = int(round(float(r) / 100 * a))

            progress.asked = a
            progress.correct_answers = c
            progress.save()


        if need_to_add<=0:
            self.stdout.write('Cancelation. User already has %s word(s)' % (current_count))
            return

        self.stdout.write('Adding new words...')

        #addNewWordBulk(self, user, count):
        for x in range(0, need_to_add):
            progress = Progress.objects.addNewWord(user)
            # asked
            a = random.randint(asked-2, asked+2)
            # ratio
            r = random.randint(rating100-20, rating100+20)
            # correct
            #import pdb; pdb.set_trace()
            c = int(round(float(r) / 100 * a))

            progress.asked = a
            progress.correct_answers = c
            progress.save()

        
