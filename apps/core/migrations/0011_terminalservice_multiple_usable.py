# Generated by Django 5.0.7 on 2024-10-03 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_container_size_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='terminalservice',
            name='multiple_usable',
            field=models.BooleanField(default=False),
        ),
    ]
