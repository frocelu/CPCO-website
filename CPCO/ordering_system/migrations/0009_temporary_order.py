# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-19 02:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordering_system', '0008_auto_20170118_1631'),
    ]

    operations = [
        migrations.CreateModel(
            name='Temporary_order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=20)),
                ('order_date', models.DateField()),
                ('b_state', models.BooleanField()),
                ('l_state', models.BooleanField()),
                ('d_state', models.BooleanField()),
                ('v_state', models.BooleanField()),
                ('cost', models.IntegerField()),
                ('add_time', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
