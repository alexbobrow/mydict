# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-27 05:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_wordsecond'),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='frequency2',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='word',
            name='rank',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
