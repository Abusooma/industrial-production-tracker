# Generated by Django 5.0.6 on 2024-06-26 19:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creationpuce', '0041_remove_objectifchangeover_changement_face_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='objectifchangeover',
            name='face_du_produit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='creationpuce.faceproduit'),
        ),
    ]
