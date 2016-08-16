# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from collections import OrderedDict

import os.path
import uuid
import random


from django.db import models
from django.db.models import Avg, Q
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.



class ProgressManager(models.Manager):



    def debug(self, key, value):
        self.debug_storage[key] = value



    def addNewWord(self, user):
        """
        Adding new word in user's dictionary
        Returns Progress entry
        """

        exclude = self.filter(user=user).values('word_id')

        word = Word.objects.filter(disabled=False).exclude(id__in=exclude)[0]
        return self.create(
            user=user,
            word=word              
        )



    def addNewWordBulk(self, user, count):
        for x in range(0, count):
            self.addNewWord(user)




    def getAvgRatio(self, user):

        progress = self.filter(user=user)
        count = progress.count()

        if count>=200:
            # если больше 200 то не учитываем посл 100
            # id_minus_100 входит в диапазон посл 100
            id_minus_100 = progress.order_by('-id')[100]
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

        self.debug_storage = OrderedDict()
        

        self.ensure100(user)


        self.debug('userPorgressCount', self.userProgressCount)
       

        NEW = 0
        REPEAT = 1

        avg_ratio = self.getAvgRatio(user)
        self.debug('avg_ratio', avg_ratio)


        
        if avg_ratio < 0.5:
            action = REPEAT
        else:
            # prb <- probability
            # формула вероятности добавления нового слова
            prb = (avg_ratio-0.5)*(100/0.5)
            self.debug('new word probability', prb)
            # по вероятности определяем действие
            action = NEW if prb>=random.randint(1,100) else REPEAT
       

        str_action = 'NEW' if action == NEW else 'REPEAT'
        self.debug('action', str_action)


        if action==NEW:
            # add word
            #print "NEW"
            progress_word = self.addNewWord(user)
            progress_word.debug = self.debug_storage
            #import ipdb; ipdb.set_trace()
            return progress_word



        if action==REPEAT:

            range_start, range_end = self.getRange(self.userProgressCount)

            self.debug('range_start', range_start)

            qs = self.filter(user=user)

            if range_start is not None:
                #print('Processing range end')
                # это слово ВХОДИТ диапазон
                word_end = self.filter(user=user).order_by('-id')[range_start:range_start+1][0]
                self.debug('range_start_word_id', word_end.id)
                qs = qs.filter(id__lte=word_end.id)


            self.debug('range_end', range_end)


            # слова на границах выбранного диапазона
            if range_end is not None:
                # import ipdb; ipdb.set_trace()
                # это слово НЕ входит диапазон
                word_start = self.filter(user=user).order_by('-id')[range_end:range_end+1][0]
                self.debug('range_end_word_id', word_start.id)
                qs = qs.filter(id__gt=word_start.id)



            # из диапазона выбираем топ 10% слов с наименьшим ratio
            range_count = qs.count()

            self.debug('range_count', range_count)

            #print "Range count %s" % range_count
            ten_perc = range_count // 10

            #print "ten percents %s" % ten_perc

            # непосредственно спислк слов
            words_list = qs.order_by('ratio')[0:ten_perc]
            
            self.debug('sql', str(words_list.query))


            #print words_list

            # и наконец наше слово
            progress_word = random.choice(words_list)
            progress_word.debug = self.debug_storage

            return progress_word







    def ensure100(self, user):
        """
        Ensures user has minimum 100 initial words
        """
        self.userProgressCount = Progress.objects.filter(user=user).count()

        # Если у юзера слов меньше 100, то добивем до 100
        if self.userProgressCount<100:
            self.addNewWordBulk(user, 100-self.userProgressCount)
            count = Progress.objects.filter(user=user).count()
            if count<100:
                raise Exception("Can't add first 100 words")





    def getRange(self, count):

        range_rand = random.randint(1, 100)
        
        # начало диапазона (при обратной сортировке по id)
        range_start = None

        # конец диапазона (при обратной сортировке по id)
        # зачастую None, это значит от range_start и до конца таблицы
        range_end = None
        

        # вычисляем границы диапазонов


        # меньше 200 слов -> используем все слова
        # if count<200:
        #    range_end = None
        #    range_start = None

        # от 200 до 650
        if count>=200 and count<650:
            # 50% вероятности 0-100
            if range_rand<=50:
                range_start = 0
                range_end = 100
            # 50% вероятности 100-x
            else:
                range_start = 100
                range_end = None

        # от 650 до 1000
        elif count>=650 and count<1000:
            # 50% вероятности 0-100
            if range_rand<=50:
                range_start = 0
                range_end = 100
            # 25% вероятности 100-200
            elif range_rand<=75:
                range_start = 100
                range_end = 200
            # 25% вероятности 200-x
            else:
                range_start = 200
                range_end = None
        
        # больше 1000
        elif count>=1000:
            # 50% вероятности 0-100
            if range_rand<=50:
                range_start = 0
                range_end = 100
            # 25% вероятности 100-300
            elif range_rand<=75:
                range_start = 100
                range_end = 300
            # 25% вероятности 300-x
            else:
                range_start = 300
                range_end = None

        return (range_start, range_end)








def pronounce_full_path(instance, filename):
    if not instance.id:
        raise Exception('Uploading pronounce is not suppored at word creation time')

    ext = os.path.splitext(filename)[1]
    filename = '%07d-%s' % (instance.id, uuid.uuid4().hex[:8])
    basename = filename + ext

    return os.path.join('pronounce', basename)








class WordManager(models.Manager):

    def getSuggest(self, text):
        if len(text)<1:
            return []

        text_mass = text.split()
        qs = self.all()
        for text_part in text_mass:
            text_part2 = " %s" % text_part
            qs = qs.filter(Q(translation__startswith=text_part) | Q(translation__contains=text_part2))
        return qs[0:10]






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

    def __str__(self):
        return self.word








class Progress(models.Model):
    word = models.ForeignKey(Word)
    user = models.ForeignKey(User)
    asked = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    ratio = models.DecimalField(default=0, max_digits=10, decimal_places=9)

    objects = ProgressManager()

    def __str__(self):
        return "id:%s / word_id:%s" % (self.id, self.word_id)


    def save(self, *args, **kwargs):

        update = False

        # getting old object to find out if ratio field
        # needs to be updated
        try:
            old = Progress.objects.get(pk=self.pk)
            if (
                old.asked != self.asked or
                old.correct_answers != self.correct_answers
            ):
                # if asked/correct_answers changed - must update ratio
                update = True
        except Progress.DoesNotExist: 
            # if new and asked/correct_answers not 0
            # must update ratio too 
            if self.asked>0 or self.correct_answers>0:
                update = True


        # update ratio if needed
        if update:
            if self.correct_answers==0:
                ratio = 0
            else:
                ratio = self.correct_answers / self.asked

            if ratio>1:
                raise Exception('Wrong ratio (word %s) %s / %s = %s' % (self.pk, self.asked, self.correct_answers, ratio))
            
            self.ratio = ratio


        # parent save method
        return super(Progress, self).save(*args, **kwargs)




