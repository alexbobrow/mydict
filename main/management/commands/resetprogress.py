import random

from django.core.management.base import BaseCommand, CommandError
from main.models import Progress
from django.contrib.auth.models import User

class Command(BaseCommand):
    
    help = 'Reset progress list for user'

    def handle(self, *args, **options):


        uid = input('Enter user id: ')
        user = User.objects.get(id=uid)

        self.stdout.write('User %s selected: ' % user)

        current_count = user.progress_set.count()
        if (current_count<=0):
            self.stdout.write('Cancelation. No words in user progress list')
            return

        self.stdout.write('User has %s word(s) in progress list' % current_count)
        confirm = input('Are you sure you want to delete progress list? (yes/no): ')

        if confirm=='yes':
            user.progress_set.all().delete()
            self.stdout.write('Deleted')
        else:
            self.stdout.write('Canceled')

        
