# Generated by Django 5.0.4 on 2024-06-27 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='lineup',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
