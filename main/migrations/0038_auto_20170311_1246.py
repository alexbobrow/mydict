# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-11 12:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0037_auto_20170224_1821'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='progress',
            name='user_comment',
        ),
        migrations.RemoveField(
            model_name='progress',
            name='user_word',
        ),
    ]
