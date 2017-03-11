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



    def get_random_entry(self, qs):
        count = qs.count()
        rand = random.randint(0,count-1)
        return qs[rand]


    def get_next(self, request):

        user = request.user

        if user.is_authenticated:

            # shown words are present in Progress model
            # first we try to find words that are not showed
            exclude = Progress.objects.filter(user=user, added=True).values('word_id')
            #words = Word.objects.filter(disabled=False).exclude(id__in=exclude)
            words = Word.objects.filter(disabled=False).filter(id__gt=100, id__lt=110)
            count = words.count()

            if count > 0:
                # have not showed words
                word = self.get_random_entry(words)
            else:
                # all words shoed. Now must give priority to words with less `showed`
                # TODO add suitable indexes, potentially show queries
                qs = Progress.objects.filter(user=user, word__isnull=False, word__disabled=False)
                mini = qs.aggregate(Min('showed'))
                mini = mini['showed__min']

                qs = qs.filter(showed=mini)
                progress = self.get_random_entry(qs)
                word = progress.word

            progess, created = Progress.objects.get_or_create(
                user=user,
                word=word,
                defaults={'showed':1}
            )

            if not created:
                progess.showed = progess.showed + 1
                progess.save()

            # cache prgress, used in get_added() and get_translation()
            word._current_progress = progess

        else:          
            qs = self.filter(disabled=False)
            word = self.get_random_entry(qs)


        return word





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
        if self._current_progress and self._current_progress.user_translation != '':
            return self._current_progress.user_translation
        else:
            return self.translation


    def get_added(self):
        # only works for word went through WordManager.get_next()
        if self._current_progress:
            return self._current_progress.added
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


    def get_random_entry(self, qs):
        count = qs.count()
        rand = random.randint(0,count-1)
        return qs[rand]



    def get_next(self, request):

        qs = Progress.objects.filter(user=request.user, added=True)
        count = qs.count()
        if count>0:

            mini = qs.aggregate(Min('showed'))
            mini = mini['showed__min']
            qs = qs.filter(showed=mini)

            progress = self.get_random_entry(qs)
            word = progress.word

            progress.showed = progress.showed + 1
            progress.save()

            return progress
        
        else:
            raise Progress.DoesNotExist()




class Progress(models.Model):
    word = models.ForeignKey(Word, null=True)
    user = models.ForeignKey(User)
    showed = models.PositiveIntegerField(default=0)
    added = models.BooleanField(default=False)   

    user_translation = models.CharField(max_length=255)

    objects = ProgressManager()




    def get_translation(self):
        
        if self.user_translation != '':
            return self.user_translation
        else:
            return self.word.translation


    
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