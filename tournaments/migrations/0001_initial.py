# Generated by Django 5.0.1 on 2024-12-07 04:02

import datetime
import django.db.models.deletion
import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clubs', '0001_initial'),
        ('matches', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Championship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('finished', 'Finished')], default='pending', max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('match_time', models.TimeField(default=datetime.time(18, 0), help_text='Match start time (UTC)')),
            ],
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(help_text='Порядковый номер сезона', unique=True)),
                ('name', models.CharField(max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('is_active', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='ChampionshipMatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round', models.PositiveIntegerField()),
                ('match_day', models.PositiveIntegerField()),
                ('processed', models.BooleanField(default=False)),
                ('championship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournaments.championship')),
                ('match', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='matches.match')),
            ],
            options={
                'ordering': ['round', 'match_day'],
            },
        ),
        migrations.CreateModel(
            name='ChampionshipTeam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.PositiveIntegerField(default=0)),
                ('matches_played', models.PositiveIntegerField(default=0)),
                ('wins', models.PositiveIntegerField(default=0)),
                ('draws', models.PositiveIntegerField(default=0)),
                ('losses', models.PositiveIntegerField(default=0)),
                ('goals_for', models.PositiveIntegerField(default=0)),
                ('goals_against', models.PositiveIntegerField(default=0)),
                ('championship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournaments.championship')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club')),
            ],
            options={
                'ordering': ['-points', '-goals_for'],
                'unique_together': {('championship', 'team')},
            },
        ),
        migrations.AddField(
            model_name='championship',
            name='teams',
            field=models.ManyToManyField(through='tournaments.ChampionshipTeam', to='clubs.club'),
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('level', models.PositiveIntegerField()),
                ('max_teams', models.PositiveIntegerField(default=16)),
                ('foreign_players_limit', models.PositiveIntegerField(default=5, help_text='Maximum number of foreign players allowed in match squad')),
            ],
            options={
                'ordering': ['country', 'level'],
                'unique_together': {('country', 'level')},
            },
        ),
        migrations.AddField(
            model_name='championship',
            name='league',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournaments.league'),
        ),
        migrations.AddField(
            model_name='championship',
            name='season',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournaments.season'),
        ),
        migrations.AlterUniqueTogether(
            name='championship',
            unique_together={('season', 'league')},
        ),
    ]
