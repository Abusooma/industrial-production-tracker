# Generated by Django 5.0.6 on 2024-05-29 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creationpuce', '0007_remove_moyen_type_arret_production_commentaire_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='arret',
            name='heure_et_minute',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
