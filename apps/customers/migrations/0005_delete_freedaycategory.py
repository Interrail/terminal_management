# Generated by Django 5.0.7 on 2024-09-27 06:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0004_remove_companycontract_free_days'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FreeDayCategory',
        ),
    ]
