# Generated by Django 5.0.6 on 2024-06-08 12:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creationpuce', '0026_tempsdecycle_produit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tempsdecycle',
            name='production',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='creationpuce.production'),
        ),
    ]
