# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-25 21:24
from __future__ import unicode_literals

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0011_auto_20160425_1939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productbase',
            name='manual_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='Prix manuel'),
        ),
    ]
