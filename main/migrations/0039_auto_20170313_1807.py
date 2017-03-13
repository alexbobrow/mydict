# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-13 18:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0038_auto_20170311_1246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progress',
            name='added',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='progress',
            name='word',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Word'),
        ),
    ]
