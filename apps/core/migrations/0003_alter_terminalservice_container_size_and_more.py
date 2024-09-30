# Generated by Django 5.0.7 on 2024-09-26 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_terminalservicetype_unit_of_measure'),
    ]

    operations = [
        migrations.AlterField(
            model_name='terminalservice',
            name='container_size',
            field=models.CharField(choices=[('20', '20 ft Standard'), ('20HC', '20 ft High Cube'), ('40', '40 ft Standard'), ('40HC', '40 ft High Cube'), ('45', '45 ft High Cube')], default='ANY', max_length=50),
        ),
        migrations.AlterField(
            model_name='terminalservice',
            name='container_state',
            field=models.CharField(choices=[('loaded', 'loaded'), ('empty', 'empty')], default='ANY', max_length=6),
        ),
        migrations.AlterField(
            model_name='terminalservicetype',
            name='unit_of_measure',
            field=models.CharField(choices=[('container', 'контейнер'), ('day', 'день'), ('operation', 'операция'), ('unit', 'единица')], max_length=50),
        ),
    ]
