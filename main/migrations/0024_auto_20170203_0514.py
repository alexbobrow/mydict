# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-02-03 05:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_word'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progress',
            name='word',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Word'),
        ),
    ]
