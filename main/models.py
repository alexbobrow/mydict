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



class ProgressManager(models.Manager):




    def addNewWord(self, user):
        word = self.all().filter(disabled=False)[0]
        return self.create(
            user=user,
            word=word              
        )



    def addNewWordBulk(self, user, count):
        for x in range(1, count):
            self.addNewWord(user)




    def getAvgRatio(self, user):

        progress = self.filter(user=user)

        if count>=200:
            # если больше 200 то не учитываем посл 100
            id_minus_100 = progress.order_by('-id')[100:1]
            return progress.filter(id__lt=id_minus_100.id).aggregate(ratio=Avg('ratio'))['ratio']
        else:
            # учитываем все
            return progress.aggregate(ratio=Avg('ratio'))['ratio']




    def getNext(self, user):

        """
        Функция выдачи следующего слова для показа / теста

        Сначала проверяем наличие 100 слов
        Если меньше, добиваем до сотни
        
        Далее
        Выбираем добавляем мы новое слово в словарь или нет
        Алгоритм такой. Вычисляем среднее значение ratio (далее avg_ratio)
        изученых слов (если слов 200 и более то без учёта последних 100 слов)
        
        Алгоритм выдачи следующего слова:
        Вероятность добавления нового слова в зависимости от avg_ratio
        1 - 100%
        0.5 - 0%
        
        Составляем формулу:
        нормализуем до 0.5->0
        nval = 0.5 нормализованный максимум
        ndelta = 0.5 нормализующее смещение
        x = (y-ndelta)*(100/nval)

        Алгоритм выбора слова для повторения
        в зависимости от кол-ва слов у юзера

        100-200
            полный рандом
        200-650
            50% последние 100-0 (order by id desc limit 0 100)
            50% последние x-100 (все остальные)
        650-1000
            50% последние 100-0 (order by id desc limit 0 100)
            25% последние 200-100 (order by id desc limit 100 100)
            25% последние x-200 (все остальные)
        1000-
            50% последние 100-0 (order by id desc limit 0 100)
            25% последние 300-100 (order by id desc limit 100 200)
            25% последние x-300 (все остальные)
        """
        
        self._ensure100(user)
        

        NOT_SET = 0
        REPEAT = 1

        avg_ratio = self.getAvgRatio(user)

        
        if avg_ratio < 0.5:
            action = REPEAT
        else:
            # prb <- probability
            # формула вероятности добавления нового слова
            prb = (avg_ratio-ndelta)*(100/0.5)
            # по вероятности определяем действие
            action = NEW if prb>=random(1,100) else REPEAT
       


        if action==NEW:
            # add word
            return self.addNewWord(user)



        if action==REPEAT:

            range_start, range_end = self._getRange(count)

            # слова на границах выбранного диапазона
            word_start = self.all().order_by('-id')[range_start:1]
            word_end = self.all().order_by('-id')[range_end:1]

            # из диапазона выбираем топ 10% слов с наименьшим ratio
            range_count = self.all().filter(id__gt=word_start.id, id__lt=word_end.id).count()
            ten_perc = range_count // 10

            # непосредственно спислк слов
            words_list = self.all().filter(id__gt=word_start.id, id__lt=word_end.id).order_by('-ratio')[0:ten_perc]

            # и наконец наше слово
            word = random.choice(words_list)

            return word







    def _ensure100(self, user):
        """
        Ensures user has minimum 100 initial words
        """
        count = Progress.objects.filter(user=user).count()

        # Если у юзера слов меньше 100, то добивем до 100
        if count<100:
            self.addNewWord(user, 100-count)
            count = Progress.objects.filter(user=user).count()
            if count<100:
                raise Exception("Can't add first 100 words")





    def _getRange(self, count):

        range_rand = random.randint(1, 100)
        range_start = None
        range_end = None

        # вычисляем границы диапазонов

        # идентично если включить эти строки
        # меньше 200 слов -> используем все слова
        # if count<200:
        #    range_start = None
        #    range_end = None

        # от 200 до 650
        if count>=200 and count<650:
            # 50% вероятности 100-0
            if range_rand<=50:
                range_start = 100
                range_end = 0
            # 50% вероятности x-100
            else:
                range_start = None
                range_end = 100

        # от 650 до 1000
        elif count>=650 and count<1000:
            # 50% вероятности 100-0
            if range_rand<=50:
                range_start = 100
                range_end = 0
            # 25% вероятности 200-100
            elif range_rand<=75:
                range_start = 200
                range_end = 100
            # 25% вероятности х-100
            else:
                range_start = None
                range_end = 200
        
        # больше 1000
        elif count>=1000:
            # 50% вероятности 100-0
            if range_rand<=50:
                range_start = 100
                range_end = 0
            # 25% вероятности 300-100
            elif range_rand<=75:
                range_start = 300
                range_end = 100
            # 25% вероятности х-300
            else:
                range_start = None
                range_end = 300

        return (range_start, range_end)








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

    objects = ProgressManager()

