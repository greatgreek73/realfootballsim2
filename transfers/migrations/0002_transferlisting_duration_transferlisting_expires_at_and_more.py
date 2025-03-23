# Generated by Django 5.1.4 on 2025-03-20 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transfers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transferlisting',
            name='duration',
            field=models.PositiveIntegerField(choices=[(5, '5 минут'), (30, '30 минут'), (60, '60 минут')], default=30, help_text='Длительность трансфера в минутах'),
        ),
        migrations.AddField(
            model_name='transferlisting',
            name='expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transferlisting',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('expired', 'Expired')], default='active', max_length=20),
        ),
    ]
