# Generated by Django 5.0.6 on 2024-06-19 16:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creationpuce', '0036_alter_tempsdecycle_production'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tempsdecycle',
            old_name='production',
            new_name='production_step_two',
        ),
    ]
