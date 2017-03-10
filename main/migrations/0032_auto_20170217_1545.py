# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-17 15:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_progress_correct_seq'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='progresslog',
            name='progress',
        ),
        migrations.RemoveField(
            model_name='progress',
            name='asked',
        ),
        migrations.RemoveField(
            model_name='progress',
            name='correct_answers',
        ),
        migrations.RemoveField(
            model_name='progress',
            name='correct_seq',
        ),
        migrations.RemoveField(
            model_name='progress',
            name='ratio',
        ),
        migrations.AddField(
            model_name='progress',
            name='showed',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='progress',
            name='skip',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='ProgressLog',
        ),
    ]