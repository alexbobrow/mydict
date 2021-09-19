from django.contrib.auth.models import User
from django.db import models

from main.managers import ProgressManager, WordManager
from main.utils import pronounce_full_path


class Word(models.Model):
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
        
    def __str__(self):
        return self.word


class Progress(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    know_count = models.PositiveIntegerField(default=0)
    know_first = models.PositiveIntegerField(default=0)
    know_avg = models.DecimalField(default=0, max_digits=10, decimal_places=9)
    know_last = models.PositiveIntegerField(default=0)

    time_updated = models.DateTimeField(auto_now=True)

    objects = ProgressManager()

    def __str__(self):
        return "id:%s / word_id:%s" % (self.id, self.word_id)

    def add_answer(self, value):
        if value not in '12345':
            raise Exception('Wrong answer value')

        new_count = self.know_count + 1
        new_avg = ((self.know_avg * self.know_count) + int(value)) / new_count

        if self.know_count == 0:
            self.know_first = value    

        self.know_count = new_count
        self.know_last = value
        self.know_avg = new_avg
       
        self.save()


class Report(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField(max_length=500)

    def __str__(self):
        return str(self.time_created)


class Preferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    show_sidebar = models.BooleanField(default=False)
    filters = models.CharField(max_length=10, default='')
    answer_delay = models.BooleanField(default=False)
