# Generated by Django 5.0.6 on 2025-06-20 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0002_project_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeentry',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
