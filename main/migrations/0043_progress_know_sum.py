# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-11 12:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0042_progresslog'),
    ]

    operations = [
        migrations.AddField(
            model_name='progress',
            name='know_sum',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
