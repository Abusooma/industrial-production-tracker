# Generated by Django 5.0.6 on 2024-06-15 15:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creationpuce', '0033_arretdeproduction_action'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='produit',
            name='defaults',
        ),
        migrations.RemoveField(
            model_name='produit',
            name='face_produit',
        ),
        migrations.RemoveField(
            model_name='produit',
            name='quantity_fc',
        ),
        migrations.RemoveField(
            model_name='produit',
            name='quantity_fs',
        ),
    ]
