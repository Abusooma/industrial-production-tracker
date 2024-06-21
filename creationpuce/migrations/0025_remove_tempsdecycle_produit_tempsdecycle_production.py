# Generated by Django 5.0.6 on 2024-06-08 12:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creationpuce', '0024_alter_tempsdecycle_tcm'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tempsdecycle',
            name='produit',
        ),
        migrations.AddField(
            model_name='tempsdecycle',
            name='production',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='creationpuce.production'),
        ),
    ]
