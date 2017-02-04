# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-24 15:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ordering_system', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='add_time',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='temp_order',
            name='add_time',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='user_default_order_state',
            name='update_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
