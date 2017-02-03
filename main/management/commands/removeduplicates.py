from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from main.models import Translation, Pronounce, WordOs, WordWf
#from django.contrib.auth.models import User



class Command(BaseCommand):
    
    help = 'Remove exactly same en word from source dict'
    """
    World Frequency 5000 free contains a lot of duplicates
    Fing all duplacates anf only left one word with the most frequency
    And delete left words
    """

    def handle(self, *args, **options):
	
    	dups = WordWf.objects.values('word').annotate(wc=Count('word')).filter(wc__gt=1)

    	for dup in dups:

    		self.stdout.write(dup['word'])

    		qs = WordWf.objects.filter(word=dup['word']).order_by('-frequency')[1:]
    		for x in qs:
    			x.delete()
    	
        self.stdout.write('DONE')
