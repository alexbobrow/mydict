# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-18 10:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_auto_20170217_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='old_translation',
            field=models.TextField(default='', max_length=500),
            preserve_default=False,
        ),
    ]