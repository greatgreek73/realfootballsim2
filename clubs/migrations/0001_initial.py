# Generated by Django 5.1.4 on 2025-05-05 04:00

import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Club Name')),
                ('country', django_countries.fields.CountryField(max_length=2, verbose_name='Country')),
                ('lineup', models.JSONField(blank=True, null=True)),
                ('is_bot', models.BooleanField(default=False, help_text='Indicates if this team is controlled by AI', verbose_name='Bot Team')),
                ('promoted', models.BooleanField(default=False, help_text='Команда повышена в классе')),
                ('relegated', models.BooleanField(default=False, help_text='Команда понижена в классе')),
            ],
        ),
    ]
