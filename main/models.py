# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from collections import OrderedDict

import os.path
import uuid
import random


from django.db import models
from django.db.models import Min, Avg, Q
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




class NextWordNotFound(Exception):
    pass




class WordManager(models.Manager):
    pass




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




    '''
    def get_added(self):
        # only works for word went through WordManager.get_next()
        if hasattr(self, '_current_progress'):
            return self._current_progress.added
        else:
            return False
    '''





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

        self.debug('get random entry: %s' % count)

        if count>0:
            rand = random.randint(0,count-1)
            return qs[rand]
        else:
            raise NextWordNotFound
        






    def get_next(self, user, filters='05'):


        if not user.is_authenticated:
            return self.get_random_entry(Word.objects.filter(disabled=False)), {}, []

        self.debug_storage = []


        word_qs = Word.objects.filter(disabled=False)
        progress_qs = self.filter(user=user)


        # delete words showed but not answered
        progress_qs.filter(know_last=0).delete()



        words_count = word_qs.count()
        self.debug('words_count', words_count)


        progress5 = progress_qs.filter(know_last=5).count()
        progress4 = progress_qs.filter(know_last=4).count()
        progress3 = progress_qs.filter(know_last=3).count()
        progress2 = progress_qs.filter(know_last=2).count()
        progress1 = progress_qs.filter(know_last=1).count()

        progress_count = progress1 + progress2 + progress3 + progress4 + progress5
        self.debug('progress_count', progress_count)


        self.debug('raw filetrs', filters)

        qs_type_word = True

        if filters == '':
            self.debug('filters: all words')
            qs = word_qs

        elif filters == '0':
            self.debug('filters: only new')
            progress_qs_ex = progress_qs.values('word_id')
            qs = word_qs.exclude(id__in=progress_qs_ex)

        elif '0' in filters and len(filters)>1:
           
            self.debug('filters: combo mode')

            ex = progress_qs

            opts = None

            if filters != '54321':
                # words with selected know_last
                for x in range(1,6):
                    y = str(x)
                    if not y in filters:
                        self.debug('Q filter', y)
                        if opts is None:
                            opts = Q(know_last=x)
                        else:
                            opts = opts | Q(know_last=x)
                if not opts is None:
                    ex = ex.filter(opts)


            qs = word_qs.exclude(id__in=ex.values('word_id'))

            

            self.debug(str(qs.query))

            self.debug('exclude count', ex.count())



        elif not '0' in filters:
            self.debug('filters: repeat only mode')

            qs = progress_qs

            opts = None

            if filters != '54321':
                # words with selected know_last
                for x in range(1,6):
                    y = str(x)
                    if y in filters:
                        self.debug('Q filter', y)
                        if opts is None:
                            opts = Q(know_last=x)
                        else:
                            opts = opts | Q(know_last=x)
                if not opts is None:
                    qs = qs.filter(opts)

            self.debug(str(qs.query))
            
            qs_type_word = False
                 


        if qs_type_word:
            # we got words qs
            # have to select word and add to progress if needed
            word = self.get_random_entry(qs)

            progress, created = Progress.objects.get_or_create(
                user=user,
                word=word,
                #defaults={'showed':1}
            )
        else:

            # we got progress qs
            progress = self.get_random_entry(qs)
            word = progress.word

       
        self.debug('word.id', progress.word.id)
        self.debug('progress.id', progress.id)

        data = {
            'total': words_count,
            'newTotal': (words_count - progress_count),
            'progress1': progress1,
            'progress2': progress2,
            'progress3': progress3,
            'progress4': progress4,
            'progress5': progress5,
        }



        return progress, data, self.debug_storage






class Progress(models.Model):
    word = models.ForeignKey(Word)
    user = models.ForeignKey(User)
    
    know_count = models.PositiveIntegerField(default=0)
    know_first = models.PositiveIntegerField(default=0)
    know_avg = models.DecimalField(default=0, max_digits=10, decimal_places=9)
    know_last = models.PositiveIntegerField(default=0)

    time_updated = models.DateTimeField(auto_now=True)

    objects = ProgressManager()

    
    def __str__(self):
        return "id:%s / word_id:%s" % (self.id, self.word_id)


    def add_answer(self, value):
        if not value in '12345':
            raise Exception('Wrong answer value')

        new_count = self.know_count + 1
        new_avg = ((self.know_avg * self.know_count) + int(value)) / new_count

        if self.know_count == 0:
            self.know_first = value    

        self.know_count = new_count
        self.know_last = value
        self.know_avg = new_avg
       
        self.save()

    






@python_2_unicode_compatible
class Report(models.Model):
    word = models.ForeignKey(Word)
    user = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField(max_length=500)

    def __str__(self):
        return str(self.time_created)




@python_2_unicode_compatible
class Preferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    show_sidebar = models.BooleanField(default=False)
    filters = models.CharField(max_length=10)
    explicit = models.BooleanField(default=False)
    answer_delay = models.BooleanField(default=False)
    
