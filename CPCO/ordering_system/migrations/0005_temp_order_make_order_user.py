# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-13 06:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordering_system', '0004_order_b'),
    ]

    operations = [
        migrations.AddField(
            model_name='temp_order',
            name='make_order_user',
            field=models.CharField(blank=True, max_length=7, null=True),
        ),
    ]
