# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-10 12:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0041_auto_20170407_0843'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgressLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('progress', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.Progress')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
