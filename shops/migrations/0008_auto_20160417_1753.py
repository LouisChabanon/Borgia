# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-17 15:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0007_auto_20160417_1411'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productbase',
            options={'permissions': (('list_productbase', 'Lister les produits de base'), ('retrieve_productbase', 'Afficher un produit de base'), ('change_price_productbase', "Changer le prix d'un produit de base"))},
        ),
    ]