# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-20 05:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20160520_0444'),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='frequency',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
