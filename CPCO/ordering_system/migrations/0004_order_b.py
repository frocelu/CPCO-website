# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-12 07:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordering_system', '0003_auto_20161230_1039'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order_b',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(blank=True, max_length=7, null=True)),
                ('user_name', models.CharField(max_length=10)),
                ('order_date', models.DateField()),
                ('b_state', models.BooleanField()),
                ('add_time', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
