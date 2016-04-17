# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-17 12:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0006_auto_20160415_1846'),
    ]

    operations = [
        migrations.AddField(
            model_name='productbase',
            name='is_manual',
            field=models.BooleanField(default=False, verbose_name='Gestion manuelle du prix'),
        ),
        migrations.AddField(
            model_name='productbase',
            name='manual_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Prix manuel'),
        ),
    ]
