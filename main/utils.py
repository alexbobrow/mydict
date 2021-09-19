import os
import uuid


def pronounce_full_path(instance, filename):
    if not instance.id:
        raise Exception('Uploading pronounce is not supported at word creation time')

    ext = os.path.splitext(filename)[1]
    filename = '%07d-%s' % (instance.id, uuid.uuid4().hex[:8])
    basename = filename + ext

    return os.path.join('pronounce', basename)


def get_next_word(user, filters):
    from main.models import Word, Progress

    words_qs = Word.objects.active()

    if not user.is_authenticated:
        # All words needed, as guests doesn't support filtering
        return words_qs.get_random_entry()

    if filters == '':
        # All words needed as no filters specified
        return words_qs.get_random_entry()

    progress_qs = Progress.objects.for_user(user)

    if filters == '0':
        # Only new words needed, exclude words with progress
        words_qs = words_qs.exclude(id__in=progress_qs.values('word_id'))
        return words_qs.get_random_entry()

    all_know_values_set = set('12345')

    if '0' in filters:
        """
        New words and words with certain know value needed. Need to
        exclude words with know value that not specified in filter.
        E.g. specified filter: 1,2,3 - need to exclude words with know value 4,5
        """
        exclude_values = all_know_values_set - set(filters)
        progress_qs = progress_qs.with_certain_know_values(exclude_values)
        words_qs = words_qs.exclude(id__in=progress_qs.values('word_id'))
        return words_qs.get_random_entry()

    # Words with certain know value needed. Need to filter words by know value specified in filter
    progress_qs = progress_qs.with_certain_know_values(list(filters))
    words_qs = words_qs.filter(id__in=progress_qs.values('word_id'))
    return words_qs.get_random_entry()


def get_progress_stats(user):
    from main.models import Progress, Word
    progress_qs = Progress.objects.for_user(user)
    stats = {}
    progress_total = 0
    for x in range(1, 6):
        count = progress_qs.filter(know_last=x).count()
        stats[f'progress{x}'] = count
        progress_total += count
    stats['total'] = Word.objects.active().count()
    stats['newTotal'] = stats['total'] - progress_total
    return stats
