# Generated by Django 5.0.7 on 2024-10-03 07:04

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('containers', '0003_alter_containerstorage_container_state'),
        ('customers', '0008_companycontract_free_days'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='containerstorage',
            name='active_services',
        ),
        migrations.CreateModel(
            name='ContainerService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('performed_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('notes', models.TextField(blank=True, default='')),
                ('container_storage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='containers.containerstorage')),
                ('contract_service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='customers.contractservice')),
            ],
            options={
                'verbose_name': 'Container Service',
                'verbose_name_plural': 'Container Services',
                'db_table': 'container_service',
                'ordering': ['-performed_at'],
            },
        ),
    ]
