# Generated by Django 5.0.7 on 2024-09-27 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_terminalservicetype_unit_of_measure'),
    ]

    operations = [
        migrations.CreateModel(
            name='FreeDayCombination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('container_size', models.CharField(choices=[('20', '20 ft Standard'), ('20HC', '20 ft High Cube'), ('40', '40 ft Standard'), ('40HC', '40 ft High Cube'), ('45', '45 ft High Cube')], max_length=50)),
                ('container_state', models.CharField(choices=[('loaded', 'loaded'), ('empty', 'empty')], max_length=6)),
                ('category', models.CharField(choices=[('import', 'Import'), ('export', 'Export'), ('transit', 'Transit')], max_length=10)),
                ('default_free_days', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Free Day Combination',
                'verbose_name_plural': 'Free Day Combinations',
                'unique_together': {('container_size', 'container_state', 'category')},
            },
        ),
    ]
