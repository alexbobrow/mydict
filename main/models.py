# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from collections import OrderedDict

import os.path
import uuid
import random


from django.db import models
from django.db.models import Min
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.


   


def pronounce_full_path(instance, filename):
    if not instance.id:
        raise Exception('Uploading pronounce is not suppored at word creation time')

    ext = os.path.splitext(filename)[1]
    filename = '%07d-%s' % (instance.id, uuid.uuid4().hex[:8])
    basename = filename + ext

    return os.path.join('pronounce', basename)



class WordManager(models.Manager):



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



        

        
    def get_random_entry(self, qs):
        count = qs.count()
        if count>0:
            rand = random.randint(0,count-1)
            return qs[rand]
        else:
            raise self.model.DoesNotExist
        



    def get_avg_ratio(self, user):

        progress = self.filter(user=user)
        #count = progress.count()

        return progress.aggregate(know_avg=Avg('know_avg'))['know_avg']

        '''
        if count>=200:
            # если больше 200 то не учитываем посл 100
            # id_minus_100 входит в диапазон посл 100
            id_minus_100 = progress.order_by('-id')[100]
            return progress.filter(id__lt=id_minus_100.id).aggregate(ratio=Avg('ratio'))['ratio']
        else:
            # учитываем все
            return progress.aggregate(ratio=Avg('ratio'))['ratio']
        '''





    def get_next(self, user):


        if not user.is_authenticated:
            return get_random_entry(Word.filter(disabled=False)), []


        """
        Функция выдачи следующего слова для показа / теста

        Сначала проверяем наличие 100 слов
        Если меньше, добиваем до сотни
        
        Далее
        Выбираем добавляем мы новое слово в словарь или нет
        Если среднее значения знания слов больше 4 то новое, если нет то повтор
        
        Алгоритм выбора слова для повторения
        в зависимости от кол-ва слов у юзера

        100-200
            полный рандом
        200-650
            90% последние 100-0 (order by id desc limit 0 100)
            10% последние x-100 (все остальные)
        650-1000
            85% последние 100-0 (order by id desc limit 0 100)
            15% последние x-100 (все остальные)
        1000-
            80% последние 100-0 (order by id desc limit 0 100)
            20% последние x-100 (все остальные)
        """

        #self.debug_storage = []
        

        self.ensure100(user)

        self.debug('user dict count', self.userProgressCount)


        NEW = 0
        REPEAT = 14
        

        avg_ratio = self.get_avg_ratio(user)
        
        self.debug('avg_ratio', avg_ratio)

        
        if avg_ratio >= 4:
            action = NEW
        else:
            action = REPEAT      

        str_action = 'NEW' if action == NEW else 'REPEAT'
        self.debug('action', str_action)

        if action==NEW:
            # add word
            #print "NEW"
            
            progress_word = self.add_new_word(user)
            #progress_word.debug = self.debug_storage
            

        if action==REPEAT:

            range_start, range_end = self.get_range(self.userProgressCount)

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
            '''
            log_arr = ProgressLog.objects.get_array(user)
            qs = qs.exclude(id__in=log_arr)
            self.debug('log', log_arr)
            '''


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
            


        #ProgressLog.objects.add(progress_word)
       
        self.debug('word.id', progress_word.word.id)
        self.debug('progress.id', progress_word.id)

        return progress_word, self.debug_storage






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





    def get_range(self, count):

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


        # от 200 и более
        if count>=200:
            self.debug("range mode 2 / 200-649 words (50/50)")
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

        return (range_start, range_end)







    '''
    def get_next(self, request):

        user = request.user

        if user.is_authenticated:





        else:
            word = self.get_random_entry(self.filter(disabled=False))
            context = {}


        return word, context
    '''




@python_2_unicode_compatible
class Word(models.Model):
    """
    Main base generated from WordOS, WordWf, Translation and pronouce
    """
    word = models.CharField(max_length=255)
    translation = models.TextField(max_length=500, null=True, default=None)
    old_translation = models.TextField(max_length=500)
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



    def get_translation(self):
        # only works for word went through WordManager.get_next()
        if hasattr(self, '_current_progress') and self._current_progress.user_translation != '':
            return self._current_progress.user_translation
        else:
            return self.translation


    def get_added(self):
        # only works for word went through WordManager.get_next()
        if hasattr(self, '_current_progress'):
            return self._current_progress.added
        else:
            return False


    def get_translation_list(self):
        if self.progress_set.all():
            progress = self.progress_set.all()[0]
            if progress.user_translation:
                return progress.user_translation
            else:
                return self.translation
        else:
            return self.translation


    def get_translation_custom_list(self):
        if self.progress_set.all():
            progress = self.progress_set.all()[0]
            if progress.user_translation:
                return True
            else:
                return False
        else:
            return False




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




class ProgressManager(models.Manager):
    pass



class Progress(models.Model):
    word = models.ForeignKey(Word)
    user = models.ForeignKey(User)
    
    showed = models.PositiveIntegerField(default=0)
    
    know_1 = models.PositiveIntegerField(default=0)
    know_2 = models.PositiveIntegerField(default=0)
    know_3 = models.PositiveIntegerField(default=0)
    know_4 = models.PositiveIntegerField(default=0)
    know_5 = models.PositiveIntegerField(default=0)
    know_avg = models.DecimalField(default=0, max_digits=10, decimal_places=9)
    know_max = models.PositiveIntegerField(default=0)
    

    user_translation = models.CharField(max_length=255)
    time_updated = models.DateTimeField(auto_now=True)

    objects = ProgressManager()

    
    def __str__(self):
        return "id:%s / word_id:%s" % (self.id, self.word_id)







@python_2_unicode_compatible
class Report(models.Model):
    word = models.ForeignKey(Word)
    user = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField(max_length=500)

    def __str__(self):
        return str(self.time_created)