# Generated by Django 5.0.6 on 2024-06-04 17:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creationpuce', '0017_alter_production_face_du_produit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='production',
            name='face_du_produit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='creationpuce.faceproduit'),
        ),
    ]
