# Generated by Django 5.0.6 on 2024-06-19 15:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creationpuce', '0035_remove_production_client_remove_production_defaults_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tempsdecycle',
            name='production',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='creationpuce.productionsteptwo'),
        ),
    ]
