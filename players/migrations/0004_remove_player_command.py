# Generated by Django 5.1.4 on 2025-01-07 08:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0003_player_boost_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='command',
        ),
    ]
