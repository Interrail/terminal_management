# Generated by Django 5.0.7 on 2024-09-26 05:07

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(db_index=True, max_length=255, unique=True, validators=[django.core.validators.RegexValidator('\\S', 'Name cannot be empty or just whitespace.')])),
                ('address', models.TextField(blank=True)),
                ('slug', models.SlugField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Company',
                'verbose_name_plural': 'Companies',
            },
        ),
        migrations.CreateModel(
            name='ContractService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ('quantity', models.PositiveIntegerField(default=1)),
            ],
            options={
                'verbose_name': 'Contract Service',
                'verbose_name_plural': 'Contract Services',
                'db_table': 'contract_service',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='CompanyContract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('file', models.FileField(blank=True, upload_to='contracts/')),
                ('free_days', models.PositiveIntegerField(default=0)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='customers.company')),
            ],
            options={
                'verbose_name': 'Customer Contract',
                'verbose_name_plural': 'Customer Contracts',
                'db_table': 'customer_contract',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='CompanyUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_users', to='customers.company')),
            ],
            options={
                'verbose_name': 'Company User',
                'verbose_name_plural': 'Company Users',
                'ordering': ['company', 'user'],
            },
        ),
    ]
