# Generated by Django 5.0.6 on 2024-05-28 17:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creationpuce', '0005_rename_nb_op_production_nombre_operateur_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='arret',
            old_name='heure_et_minute_de_fin',
            new_name='heure_et_minute',
        ),
        migrations.RemoveField(
            model_name='arret',
            name='heure_et_minute_du_debut',
        ),
    ]
