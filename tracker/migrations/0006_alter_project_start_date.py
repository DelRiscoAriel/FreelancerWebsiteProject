# Generated by Django 5.0.6 on 2025-06-20 17:28

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0005_project_billing_type_project_fixed_rate_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
