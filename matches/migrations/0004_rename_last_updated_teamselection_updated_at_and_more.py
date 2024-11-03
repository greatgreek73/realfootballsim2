# Generated by Django 5.0.4 on 2024-06-26 18:22

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0001_initial'),
        ('matches', '0003_rename_updated_at_teamselection_last_updated_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teamselection',
            old_name='last_updated',
            new_name='updated_at',
        ),
        migrations.AddField(
            model_name='teamselection',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='teamselection',
            name='match',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_selections', to='matches.match'),
        ),
        migrations.AlterField(
            model_name='teamselection',
            name='club',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club'),
        ),
        migrations.AlterField(
            model_name='teamselection',
            name='selection',
            field=models.JSONField(),
        ),
        migrations.AlterUniqueTogether(
            name='teamselection',
            unique_together={('match', 'club')},
        ),
    ]
