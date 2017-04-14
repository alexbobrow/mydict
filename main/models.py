# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from collections import OrderedDict

import os.path
import uuid
import random


from django.db import models
from django.db.models import Min, Avg
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

    pass

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
        

    def add_new_word(self, user):
        """
        Adding new word in user's dictionary
        Returns Progress entry
        """

        self.debug("Adding new word to user's dict")

        exclude = self.filter(user=user).values('word_id')

        word_qs = Word.objects.filter(disabled=False).exclude(id__in=exclude)
        word = self.get_random_entry(word_qs)

        return self.create(
            user=user,
            word=word              
        )



    def add_new_word_bulk(self, user, count):
        # TODO improve, not to request word lest each iteration
        for x in range(0, count):
            self.add_new_word(user)






    def get_next(self, user):


        if not user.is_authenticated:
            return self.get_random_entry(Word.objects.filter(disabled=False)), {}, []

        self.debug_storage = []

        """
        Смотрим кол-во слов с плохим уровнем знания
        Отдельно с уровнем знания <=4, отдельно <=3
        Высчитываем вероятность повторения слова на основе кол-ва слов с плохим уровнем знания
        Для урвоеня меньше <=3
        100 слов - 100% повторения
        0 слов - 0% повторения

        Для урвоеня меньше <=4
        100 слов - 30% повторения
        0 слов - 0% повторения
    
        Берем больший из двух.
        """


        words_count = Word.objects.filter(disabled=False).count()
        self.debug('words_count', words_count)

        progress_qs = self.filter(user=user)

        progress_count = progress_qs.count()
        self.debug('progress_count', progress_count)

        progress_avg = progress_qs.aggregate(know_avg=Avg('know_avg'))['know_avg']
        self.debug('progress_avg', progress_avg)

        progress4 = progress_qs.filter(know_max__lte=4).count()

        progress3 = progress_qs.filter(know_max__lte=3).count()

        # progress 3
        # 100 items -> 100% repeat
        # 0 items -> 0% repeat

        # progress 4
        # 100 items -> 33% repeat
        # 0 items -> 0% repeat

        if progress3 > 100:
            progress3 = 100

        if progress4 > 100:
            progress4 = 100

        self.debug('progress3 count', progress3)
        self.debug('progress4 count', progress4)

        progress4 = progress4 // 3

        progress_prb = progress3 if progress3 > progress4 else progress4

        self.debug('progress_prb', progress_prb)

        range_rand = random.randint(1, 100)

        self.debug('range_rand', range_rand)

        NEW = 0
        REPEAT = 14

        action = REPEAT if range_rand < progress_prb else NEW

        str_action = 'NEW' if action == NEW else 'REPEAT'
        self.debug('action', str_action)
        
  
        if action==NEW:
            # add word
            #print "NEW"
            
            progress_word = self.add_new_word(user)
            #progress_word.debug = self.debug_storage
            

        if action==REPEAT:

            qs = progress_qs.filter(know_max__lte=4)


            # отсеиваем последние 10 из лога
            log_arr = ProgressLog.objects.get_array(user)
            qs = qs.exclude(id__in=log_arr)
            
            self.debug('log', log_arr)


            # из диапазона выбираем топ 1/3 слов с наименьшим ratio
            range_count = qs.count()

            self.debug('range_count', range_count)

            #print "Range count %s" % range_count
            perc_count = range_count // 3
            if perc_count<5:
                perc_count = 5


            #print "ten percents %s" % perc_count

            # непосредственно спислк слов
            words_list = qs.order_by('know_max')[0:perc_count]
            
            self.debug('sql', str(words_list.query))


            #print words_list

            # и наконец наше слово
            progress_word = random.choice(words_list)
            #progress_word.debug = self.debug_storage
            

        # paralel requests unsafe, but not critical,
        # lets limit paralel in frontend
        ProgressLog.objects.add(progress_word)
       
        self.debug('word.id', progress_word.word.id)
        self.debug('progress.id', progress_word.id)

        data = {
            'total': words_count,
            'userprogress_count': progress_count,
        }

        if progress_avg:
            data['knowAvg'] = '%.2f' % progress_avg


        return progress_word, data, self.debug_storage






class Progress(models.Model):
    word = models.ForeignKey(Word)
    user = models.ForeignKey(User)
    
    showed = models.PositiveIntegerField(default=0)
    
    know_1 = models.PositiveIntegerField(default=0)
    know_2 = models.PositiveIntegerField(default=0)
    know_3 = models.PositiveIntegerField(default=0)
    know_4 = models.PositiveIntegerField(default=0)
    know_5 = models.PositiveIntegerField(default=0)
    know_sum = models.PositiveIntegerField(default=0)
    know_avg = models.DecimalField(default=0, max_digits=10, decimal_places=9)
    know_max = models.PositiveIntegerField(default=0)
    

    user_translation = models.CharField(max_length=255)
    time_updated = models.DateTimeField(auto_now=True)

    objects = ProgressManager()

    
    def __str__(self):
        return "id:%s / word_id:%s" % (self.id, self.word_id)


    def add_answer(self, value):
        if not value in '12345':
            raise Exception('Wrong answer value')
        field = 'know_%s' % value
        old_value = int(getattr(self, field))
        setattr(self, field, (old_value+1))
        self.save()

    

    def save(self, *args, **kwargs):

        print('progress save routine')
        
        know_max_key = 0
        know_max_value = 0

        know_list = []
        know_sum = 0
        for x in range(1,6):
            field = 'know_%s' % x
            print(field)
            know_x = getattr(self, field)
            know_sum = know_sum + know_x
            if know_x > know_max_value:
                know_max_key = x
                know_max_value = know_x

            know_list = know_list + [x] * know_x

        list_len = len(know_list)
        if list_len > 0:
            avg = sum(know_list) / float(list_len)
        else:
            avg = 0

        self.know_avg = avg
        self.know_max = know_max_key
        self.know_sum = know_sum

        print('avg %s' % avg)
        print('max %s' % know_max_key)

        res = super(Progress, self).save(*args, **kwargs)

        return res





class ProgressLogManager(models.Manager):

    def get_array(self, user):
        qs = self.filter(progress__user=user)[0:10]
        return [x.progress.pk for x in qs]


    
    def add(self, progress):
        self.create(progress=progress)
        qs = list(self.filter(progress__user=progress.user).order_by('-id'))
        qs = qs[10:]
        for log in qs:
            log.delete()




class ProgressLog(models.Model):
    # id supposed
    progress = models.OneToOneField(Progress)
    time_created = models.DateTimeField(auto_now_add=True)

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