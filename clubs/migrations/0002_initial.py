# Generated by Django 5.0.1 on 2024-12-07 04:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clubs', '0001_initial'),
        ('tournaments', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='league',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clubs', to='tournaments.league'),
        ),
        migrations.AddField(
            model_name='club',
            name='owner',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='club', to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
    ]
