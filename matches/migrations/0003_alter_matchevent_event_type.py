# Generated by Django 5.0.1 on 2024-12-07 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0002_alter_matchevent_event_type_alter_matchevent_player'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matchevent',
            name='event_type',
            field=models.CharField(choices=[('goal', 'Goal'), ('miss', 'Miss'), ('possession', 'Possession Change'), ('defense_to_midfield', 'Defense to Midfield Transition'), ('midfield_to_attack', 'Midfield to Attack Transition'), ('attack_to_shot', 'Attack to Shot Opportunity'), ('interception', 'Interception'), ('yellow_card', 'Yellow Card'), ('red_card', 'Red Card'), ('substitution', 'Substitution')], max_length=20),
        ),
    ]