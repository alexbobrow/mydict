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

    

    def debug(self, key, value=''):

        if not hasattr(self, 'debug_storage'):
            self.debug_storage = []

        if value=='':
            self.debug_storage.append(key)
        else:
            self.debug_storage.append({
                'key': key,
                'value': value
            })



    def applyDebug(self, progress_word):

        self.debug('word.id', progress_word.word.id)
        self.debug('progress.id', progress_word.id)
        self.debug('progress.asked', progress_word.asked)
        self.debug('progress.correct_answers', progress_word.correct_answers)
        self.debug('progress.ratio', progress_word.ratio)
        

        progress_word.debug = self.debug_storage

        



    def addNewWord(self, user):
        """
        Adding new word in user's dictionary
        Returns Progress entry
        """

        self.debug("Adding new word to user's dict")

        exclude = self.filter(user=user).values('word_id')

        word_qs = Word.objects.filter(disabled=False).exclude(id__in=exclude)
        word = word_qs[0]

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

        self.debug_storage = []
        

        self.ensure100(user)

        self.debug('user dict count', self.userProgressCount)

        # проверяем нет ли в логах не отвеченного слова
        unanswered = ProgressLog.objects.get_unanswered_word(user)
        if unanswered:
            self.debug('unanswered word in logs found')
            self.applyDebug(unanswered)
            return unanswered



        NEW = 0
        REPEAT = 14
        

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
            #progress_word.debug = self.debug_storage
            

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


            # отсеиваем последние 10 из лога
            log_arr = ProgressLog.objects.get_array(user)
            qs = qs.exclude(id__in=log_arr)
            self.debug('log', log_arr)


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
            #progress_word.debug = self.debug_storage
            


        ProgressLog.objects.add(progress_word)
       

        self.applyDebug(progress_word)

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

        self.debug("rand factor", range_rand)
        
        # начало диапазона (при обратной сортировке по id)
        range_start = None

        # конец диапазона (при обратной сортировке по id)
        # зачастую None, это значит от range_start и до конца таблицы
        range_end = None
        

        # вычисляем границы диапазонов

        # меньше 200 слов -> используем все слова
        if count<200:
            self.debug("range mode 1 / less than 200 / using all words")
            # range_end = None
            # range_start = None

        # от 200 до 650
        if count>=200 and count<650:
            self.debug("range mode 2 / 200-649 words")
            # 50% вероятности 0-100
            if range_rand<=50:
                self.debug("range mode 2.1 / 50% / range 0-100")
                range_start = 0
                range_end = 100
            # 50% вероятности 100-x
            else:
                self.debug("range mode 2.2 / 50% / range 100-∞")
                range_start = 100
                range_end = None

        # от 650 до 1000
        elif count>=650 and count<1000:
            self.debug("range mode 3 / 650-999 words")
            # 50% вероятности 0-100
            if range_rand<=50:
                self.debug("range mode 3.1 / 50% / range 0-100")
                range_start = 0
                range_end = 100
            # 25% вероятности 100-200
            elif range_rand<=75:
                self.debug("range mode 3.2 / 25% / range 100-200")
                range_start = 100
                range_end = 200
            # 25% вероятности 200-x
            else:
                self.debug("range mode 3.3 / 25% / range 200-∞")
                range_start = 200
                range_end = None
        
        # больше 1000
        elif count>=1000:
            self.debug("range mode 4 / 1000 and more words")
            # 50% вероятности 0-100
            if range_rand<=50:
                self.debug("range mode 4.1 / 50% / range 0-100")
                range_start = 0
                range_end = 100
            # 25% вероятности 100-300
            elif range_rand<=75:
                self.debug("range mode 4.2 / 25% / range 100-300")
                range_start = 100
                range_end = 300
            # 25% вероятности 300-x
            else:
                self.debug("range mode 4.3 / 25% / range 300-∞")
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

        # only postgres distinct
        # res = qs.distinct('translation').order_by()
       
        #res = qs[0:20]

        # distinct for all
        res = []
        unique = {}
        for model in qs:
            if not model.translation in unique:
                # caution utf-8 in dict keys
                unique[model.translation] = model.translation
                res.append(model)

        # now sort so suggestion with exact match will be on top

        def factor(x):
            trans_mass = x.translation.split(',')
            trans_mass = [x.strip() for x in trans_mass]

            # exact match
            if text == x.translation:
                return 0
            # match to one of words in translation
            elif text in trans_mass:
                return 1
            # other
            else:
                return 2

        res = sorted(res, key=lambda x: x.frequency, reverse=True)
        res = sorted(res, key=factor)

        res = res[0:10]

        return res



@python_2_unicode_compatible
class Word(models.Model):
    """
    Main base generated from WordOS, WordWf, Translation and pronouce
    """
    word = models.CharField(max_length=255)
    translation = models.TextField(max_length=500, null=True, default=None)
    base = models.CharField(max_length=255, null=True, default=None)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    frequency = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(default=0)
    pronounce = models.FileField(upload_to=pronounce_full_path, blank=True, default='')
    disabled = models.BooleanField(default=False)

    objects = WordManager()


    class Meta:
        ordering = ['rank']
        
        permissions = (
            ("tester", "Tester interfaces"),
        )

    def __str__(self):
        return self.word






@python_2_unicode_compatible
class WordOs(models.Model):
    """
    Open Subtitles resource
    """
    word = models.CharField(max_length=255)
    frequency = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.word



@python_2_unicode_compatible
class WordWf(models.Model):
    """
    Word Frequency 5000 free resource
    """
    word = models.CharField(max_length=255)
    frequency = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.word




@python_2_unicode_compatible
class Translation(models.Model):
    word = models.CharField(max_length=255, unique=True)
    translation = models.TextField(max_length=500, null=True, default=None)
    base = models.CharField(max_length=255, null=True, default=None)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    status = models.NullBooleanField()

    def __str__(self):
        return self.word



@python_2_unicode_compatible
class Pronounce(models.Model):
    word = models.CharField(max_length=255, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to=pronounce_full_path, blank=True, default='')
    status = models.NullBooleanField()

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




class ProgressLogManager(models.Manager):

    def get_array(self, user):
        qs = self.filter(progress__user=user)[0:10]
        return [x.progress.pk for x in qs]

    
    def get_unanswered_word(self, user):
        unanswered = self.filter(progress__user=user, answered=False)
        if len(unanswered)>0:
            return unanswered[0].progress
        else:
            None

    
    def add(self, progress):
        self.create(progress=progress)
        qs = list(self.filter(progress__user=progress.user).order_by('-id'))
        qs = qs[10:]
        for log in qs:
            log.delete()




class ProgressLog(models.Model):
    # id supposed
    progress = models.OneToOneField(Progress)
    answered = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    objects = ProgressLogManager()




@python_2_unicode_compatible
class Report(models.Model):
    word = models.ForeignKey(Word)
    user = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField(max_length=500)

    def __str__(self):
        return str(self.time_created)