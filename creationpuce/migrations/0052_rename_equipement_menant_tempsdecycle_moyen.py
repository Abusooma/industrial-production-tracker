# Generated by Django 5.0.6 on 2024-07-15 16:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creationpuce', '0051_produit_client'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tempsdecycle',
            old_name='equipement_menant',
            new_name='moyen',
        ),
    ]
