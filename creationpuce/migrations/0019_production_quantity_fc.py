# Generated by Django 5.0.6 on 2024-06-05 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creationpuce', '0018_alter_production_face_du_produit'),
    ]

    operations = [
        migrations.AddField(
            model_name='production',
            name='quantity_fc',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
