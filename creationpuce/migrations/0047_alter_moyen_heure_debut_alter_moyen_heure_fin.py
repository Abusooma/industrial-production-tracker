# Generated by Django 5.0.6 on 2024-07-04 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creationpuce', '0046_alter_typedechangementdeobjectif_objectif'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moyen',
            name='heure_debut',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='moyen',
            name='heure_fin',
            field=models.TimeField(blank=True, null=True),
        ),
    ]