# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-16 05:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_auto_20170211_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='progresslog',
            name='time_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]