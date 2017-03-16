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





    def qs_by_type_filter(self, request, type_filter):

            user = request.user
            base_qs = self.filter(disabled=False)

            new = type_filter[0]
            added = type_filter[1]
            removed = type_filter[2]

            progress_all = Progress.objects.filter(user=user).values('word_id')
            progress_added = Progress.objects.filter(user=user, added=True).values('word_id')
            progress_removed = Progress.objects.filter(user=user, added=False).values('word_id')


            # none
            if not new and not added and not removed:
                # unexpected
                raise Exception('Not expected request params')

            # new
            if new and not added and not removed:
                return base_qs.exclude(id__in=progress_all)

            # added
            if not new and added and not removed:
                # TODO Maybe add filtering by lowest `showed`
                # to focus on less showed words
                return base_qs.filter(id__in=progress_added)

            # removed
            if not new and not added and removed:
                return base_qs.filter(id__in=progress_removed)

            # new added
            if new and added and not removed:
                return base_qs.exclude(id__in=progress_removed)

            # new removed
            if new and not added and removed:
                return base_qs.exclude(id__in=progress_added)

            # added removed
            if not new and added and removed:
                return base_qs.filter(id__in=progress_all)

            # new added removed
            if new and added and removed:
                return base_qs





    def get_random_entry(self, qs):
        count = qs.count()
        if count>0:
            rand = random.randint(0,count-1)
            return qs[rand]
        else:
            raise self.model.DoesNotExist
        




    def get_next(self, request):

        user = request.user

        if user.is_authenticated:

            # convert '101' to [True, False, True]
            type_filter = [False if x=='0' else True for x in request.GET.get('tf', '100')]

            words = self.qs_by_type_filter(request, type_filter)
            word = self.get_random_entry(words)

            progress, created = Progress.objects.get_or_create(
                user=user,
                word=word,
                defaults={'showed':1}
            )

            if not created:
                progress.showed = progress.showed + 1
                progress.save()

            # cache prgress, used in get_added() and get_translation()
            word._current_progress = progress

        else:
            word = self.get_random_entry(self.filter(disabled=False))


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
    word = models.ForeignKey(Word)
    user = models.ForeignKey(User)
    showed = models.PositiveIntegerField(default=0)
    added = models.BooleanField(default=True)   

    user_translation = models.CharField(max_length=255)

    objects = ProgressManager()




    def get_translation(self):
        
        if self.user_translation != '':
            return self.user_translation
        else:
            return self.word.translation


    def is_changed(self):
        if self.user_translation != '':
            return True
        else:
            return False


    
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