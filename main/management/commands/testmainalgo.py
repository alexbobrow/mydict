import random

from django.core.management.base import BaseCommand, CommandError
from main.models import Progress
from django.contrib.auth.models import User

class Command(BaseCommand):
    
    help = 'Testing main algorhytm'

    def handle(self, *args, **options):

        u = User.objects.get(id=1)



        #Progress.objects.addNewWordBulk(u, 10)

        #progress = Progress.objects.filter(user=u)
        #for word in progress:
        #    word.ratio = random.randint(4,6)
        #    word.save()
        #
        #print Progress.objects.getAvgRatio(u)

        #Progress.objects.ensure100(u)

        Progress.objects.getNext(u)

