# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-27 12:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cash',
            name='date_cash',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cheque',
            name='number',
            field=models.CharField(max_length=7),
        ),
    ]
