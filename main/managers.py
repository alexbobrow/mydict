import operator
import random
from functools import reduce

from django.db import models
from django.db.models import Q

from main.exceptions import NextWordNotFound


class WordQuerySet(models.QuerySet):

    def get_random_entry(self):
        qs = self.all()
        count = qs.count()
        if count > 0:
            rand = random.randint(0, count-1)
            return qs[rand]
        else:
            raise NextWordNotFound


class WordManager(models.Manager):

    def get_queryset(self):
        return WordQuerySet(self.model, using=self._db)

    def active(self):
        return self.filter(disabled=False)


class ProgressQuerySet(models.QuerySet):

    def with_certain_know_values(self, know_values):
        query = reduce(operator.or_, (Q(know_last=know_value) for know_value in know_values))
        return self.all().filter(query)


class ProgressManager(models.Manager):

    def get_queryset(self):
        return ProgressQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.filter(user=user)

    def create_from_answer(self, user, word, answer_value):
        answer_value = int(answer_value)
        return self.create(
            user=user,
            word=word,
            know_first=answer_value,
            know_avg=answer_value,
            know_last=answer_value,
            know_count=1
        )
