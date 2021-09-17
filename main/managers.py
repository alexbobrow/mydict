import random

from django.db import models
from django.db.models import Q

from main.exceptions import NextWordNotFound


class ProgressManager(models.Manager):

    def get_random_entry(self, qs):

        count = qs.count()

        if count > 0:
            rand = random.randint(0, count-1)
            return qs[rand]
        else:
            raise NextWordNotFound

    def get_next(self, user, filters='05'):
        from main.models import Word, Progress

        if not user.is_authenticated:

            return self.get_random_entry(Word.objects.filter(disabled=False)), {}, []

        word_qs = Word.objects.filter(disabled=False)
        progress_qs = self.filter(user=user)

        # delete words showed but not answered
        progress_qs.filter(know_last=0).delete()

        words_count = word_qs.count()

        progress5 = progress_qs.filter(know_last=5).count()
        progress4 = progress_qs.filter(know_last=4).count()
        progress3 = progress_qs.filter(know_last=3).count()
        progress2 = progress_qs.filter(know_last=2).count()
        progress1 = progress_qs.filter(know_last=1).count()

        progress_count = progress1 + progress2 + progress3 + progress4 + progress5

        qs_type_word = True

        if filters == '':
            qs = word_qs

        elif filters == '0':
            progress_qs_ex = progress_qs.values('word_id')
            qs = word_qs.exclude(id__in=progress_qs_ex)

        elif '0' in filters and len(filters) > 1:

            ex = progress_qs

            opts = None

            if filters != '54321':
                # words with selected know_last
                for x in range(1, 6):
                    y = str(x)
                    if y not in filters:
                        if opts is None:
                            opts = Q(know_last=x)
                        else:
                            opts = opts | Q(know_last=x)
                if opts is not None:
                    ex = ex.filter(opts)

            qs = word_qs.exclude(id__in=ex.values('word_id'))

        elif '0' not in filters:
            qs = progress_qs
            opts = None
            if filters != '54321':
                # words with selected know_last
                for x in range(1, 6):
                    y = str(x)
                    if y in filters:
                        if opts is None:
                            opts = Q(know_last=x)
                        else:
                            opts = opts | Q(know_last=x)
                if opts is not None:
                    qs = qs.filter(opts)

            qs_type_word = False

        if qs_type_word:
            # we got words qs
            # have to select word and add to progress if needed
            word = self.get_random_entry(qs)

            progress, created = Progress.objects.get_or_create(
                user=user,
                word=word,
            )
        else:
            # we got progress qs
            progress = self.get_random_entry(qs)
            word = progress.word

        data = {
            'total': words_count,
            'newTotal': (words_count - progress_count),
            'progress1': progress1,
            'progress2': progress2,
            'progress3': progress3,
            'progress4': progress4,
            'progress5': progress5,
        }

        return progress, data, []
