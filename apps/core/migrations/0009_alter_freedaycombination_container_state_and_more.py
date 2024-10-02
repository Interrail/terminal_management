# Generated by Django 5.0.7 on 2024-10-02 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_remove_freedaycombination_test_free_days'),
    ]

    operations = [
        migrations.AlterField(
            model_name='freedaycombination',
            name='container_state',
            field=models.CharField(choices=[('loaded', 'loaded'), ('empty', 'empty'), ('any', 'any')], max_length=50),
        ),
        migrations.AlterField(
            model_name='terminalservice',
            name='container_state',
            field=models.CharField(choices=[('loaded', 'loaded'), ('empty', 'empty'), ('any', 'any')], default='ANY', max_length=6),
        ),
        migrations.AlterField(
            model_name='terminalservice',
            name='name',
            field=models.TextField(),
        ),
    ]