# Generated by Django 5.0.7 on 2024-09-26 05:07

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Yard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Yard Name')),
                ('max_rows', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('max_columns', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('max_tiers', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('x_coordinate', models.FloatField(blank=True, null=True)),
                ('z_coordinate', models.FloatField(blank=True, null=True)),
                ('rotation_degree', models.FloatField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Yard',
                'verbose_name_plural': 'Yards',
                'db_table': 'yard',
            },
        ),
        migrations.CreateModel(
            name='ContainerLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('row', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('column_start', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('column_end', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('tier', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('container', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='core.container', verbose_name='Container')),
                ('yard', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='container_locations', to='locations.yard', verbose_name='Yard')),
            ],
            options={
                'verbose_name': 'Container Location',
                'verbose_name_plural': 'Container Locations',
                'db_table': 'container_location',
            },
        ),
    ]
