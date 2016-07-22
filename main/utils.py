"""
testing
from django.contrib.auth.models import User
from main.models import Progress, Word
from main.utils import *
user = User.objects.get(id=1)
"""

from django.db.models import Min

from .models import Word, Progress


def get_user_word_count(user):
    """
    next word appear when min know_rating becomes more than 3***
    ** this number is subject to correct during testing
    """

    



def check_if_must_add(user):
    """
    Checks if we must add words to user's dict
    next word appear when min know_rating becomes more than 'min_rating_to_progress'
    """

    # this number is subject to correct during testing for the best UX
    min_rating_to_progress = 3

    current_min_rating = Progress.objects.filter(user=user).aggregate(Min('know_rating'))['know_rating__min']

    return current_min_rating >= min_rating_to_progress




def add_initial_words(user):
    """
    Adds initial first 100 words when user just start to learn and
    have zero LWQ
    """
    next_words = Word.objects.order_by('rank')[:100]

    for next_word in next_words:
        new_word = Progress.objects.create(user=user, word=next_word)

    return True        





def check_user_dict(user):
    """
    checks if user's dict meet his current user's learning words quantity (hereafter LWQ)
    and adds words if ncessary
    next word appear when min know_rating becomes more than 'min_rating_to_progress'
    """

    current_lwq = Progress.objects.filter(user=user).count()

    if (current_lwq>0 and current_lwq<100):
        raise Exception('Unexpected LWQ')



    # special case - initial adding first 100 words
    if (current_lwq==0):
        return add_initial_words(user)



    # standart case - add word if minimum know rating is ok
    must_add = check_if_must_add(user)

    while must_add:

        # subquery
        progress_ids = Progress.objects.filter(user=user).values_list('id', flat=True)

        # get next word that not in user dict
        next_word = Word.objects.exclude(id__in=progress_ids).order_by('rank').first()

        Progress.objects.create(user=user, word=next_word)

        must_add = check_if_must_add(user)

    return True
