# Generated by Django 5.0.6 on 2024-06-04 17:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creationpuce', '0015_alter_production_face_du_produit'),
    ]

    operations = [
        migrations.CreateModel(
            name='FaceProduit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=25)),
                ('secteur', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='creationpuce.secteur')),
            ],
        ),
        migrations.AlterField(
            model_name='production',
            name='face_du_produit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='creationpuce.faceproduit'),
        ),
    ]
