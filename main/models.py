# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division

import os.path
import uuid
import random


from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.



class WordManager(models.Manager):


    def addNewWord(self, user, count=1):

        words = self.all().filter(disabled=False)[0:count]

        for word in words:
            Progress.objects.create(
                user=user,
                word=word              
            )



    def getNext(self, user):

        """
        Функция выдачи следующего слова для показа / теста

        Проверяем наличия 100 слов

        Выбираем добавляем мы новое слово в словарь или нет
        Алгоритм такой. Вычисляем среднее значение ratio изученых слов
        (если слов 200 и более то без учёта последних 100 слов)
        Алгоритм выдачи следующего слова:
        Далее по формуле - вероятность появления нового слова
        1 - 100%
        0.5 - 0%
        то есть
        1->0.5 
        100->0
        нормализуем до 0.5->0:
        nval = 0.5 нормализованный максимум
        ndelta = 0.5 нормализующее смещение
        x = (y-ndelta)*(100/nval)

        Алгоритм выбора слова для повторения
        в зависимости от кол-ва слов у юзера

        100-200
            полный рандом
        200-650
            50% последние 100-0
            50% последние x-100 (все остальные)
        650-1000
            50% последние 100-0
            25% последние 200-100
            25% последние x-200 (все остальные)
        1000-
            50% последние 100-0
            25% последние 300-100
            25% последние x-300 (все остальные)
        """
        
        
        

        NOT_SET = 0
        REPEAT = 1
        NEW = 2

        action = NOT_SET


        count = self.filter(user=user).count()

        # Если у юзера слов меньше 100, то добивем до 100
        if count<100:
            self.addNewWord(user, 100-count)
            count = self.filter(user=user).count()
            if count<100:
                raise Exception("Can't add first 100 words")


        if count>=200:
            # если больще 200 то не учитываем посл 100
            # id_minus_100 = self.all().order_by('-id')[100:1]
            # avg_ratio = self.all().filter(id__lt=id_minus_100.id).aggregate(ratio=Avg('ratio'))['ratio']
            avg_ratio = self.all().aggregate(ratio=Avg('ratio'))['ratio']
        else:
            # учитываем все
            avg_ratio = self.all().aggregate(ratio=Avg('ratio'))['ratio']


        
        if avg_ratio < 0.5:
            action = REPEAT
        else:
            #probability
            prb = (avg_ratio-ndelta)*(100/0.5)
            action = NEW if prb>=random(1,100) else REPEAT

        
        if action==NEW:
            # add word
            # return new word
            return


        range_rand = random.randint(1, 100)
        range_start = None
        range_end = None


        if action==REPEAT:
            # если слов 
            # if count<200:
            #    range_start = None
            #    range_end = None
            if count>=200 and count<650:
                if range_rand<=50:
                    range_start = 100
                    range_end = 0
                else:
                    range_start = None
                    range_end = 100
            elif count>=650 and count<1000:
                if range_rand<=50:
                    range_start = 100
                    range_end = 0
                elif range_rand<=75:
                    range_start = 200
                    range_end = 100
                else:
                    range_start = None
                    range_end = 200
            elif count>=1000:
                if range_rand<=50:
                    range_start = 100
                    range_end = 0
                elif range_rand<=75:
                    range_start = 300
                    range_end = 100
                else:
                    range_start = None
                    range_end = 300


            # слова на границах выбранного диапазона
            word_start = self.all().order_by('-id')[range_start:1]
            word_end = self.all().order_by('-id')[range_end:1]

            # из диапазона выбираем топ 10% слов с наименьшим ratio
            range_count = self.all().filter(id__gt=word_start.id, id__lt=word_end.id).count()
            ten_prec = range_count // 10

            # непосредственно спислк слов
            words_list = self.all().filter(id__gt=word_start.id, id__lt=word_end.id).order_by('-ratio')[0:ten_prec]

            # и наконец наше слово
            word = random.choice(words_list)


def nextGetRatio():
    pass





def pronounce_full_path(instance, filename):
    if not instance.id:
        raise Exception('Uploading pronounce is not suppored at word creation time')

    ext = os.path.splitext(filename)[1]
    filename = '%07d-%s' % (instance.id, uuid.uuid4().hex[:8])
    basename = filename + ext

    return os.path.join('pronounce', basename)





@python_2_unicode_compatible
class Word(models.Model):
    word = models.CharField(max_length=255)
    translation = models.TextField(max_length=500, null=True, default=None)
    #show_count = models.PositiveIntegerField(default=0, blank=True)
    #test_count = models.PositiveIntegerField(default=0, blank=True)
    #test_rating = models.PositiveIntegerField(default=0, blank=True)
    base = models.CharField(max_length=255, null=True, default=None)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    frequency = models.PositiveIntegerField(default=0)
    frequency2 = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(default=0)
    pronounce = models.FileField(upload_to=pronounce_full_path, blank=True, default='')
    gstatic = models.NullBooleanField(null=True, default=None)
    disabled = models.BooleanField(default=False)

    objects = WordManager()

    class Meta:
        ordering = ['rank']

    def __str__(self):
        return self.word



@python_2_unicode_compatible
class WordSecond(models.Model):
    word = models.CharField(max_length=255)
    translation = models.TextField(max_length=500, null=True, default=None)
    base = models.CharField(max_length=255, null=True, default=None)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    frequency = models.PositiveIntegerField(default=0)

    objects = WordManager()

    def __str__(self):
        return self.word



class Progress(models.Model):
    word = models.ForeignKey(Word)
    user = models.ForeignKey(User)
    show_count = models.PositiveIntegerField(default=0)
    answered = models.PositiveIntegerField(default=0)
    ratio = models.PositiveIntegerField(default=0)

