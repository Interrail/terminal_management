# Generated by Django 5.0.7 on 2024-09-26 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='terminalservicetype',
            name='unit_of_measure',
            field=models.CharField(choices=[('container', 'container'), ('day', 'day'), ('operation', 'Operation'), ('unit', 'unit')], max_length=50),
        ),
    ]
