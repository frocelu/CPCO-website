# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-19 07:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordering_system', '0010_auto_20170119_1048'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='none_staff_order',
            name='b_state',
        ),
        migrations.RemoveField(
            model_name='none_staff_order',
            name='d_state',
        ),
        migrations.RemoveField(
            model_name='none_staff_order',
            name='l_state',
        ),
        migrations.AddField(
            model_name='none_staff_order',
            name='l_quantity',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
