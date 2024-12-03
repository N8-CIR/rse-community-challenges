# Generated by Django 5.1.3 on 2024-11-28 20:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('challenge_name', models.CharField(max_length=200)),
                ('challenge_description', models.TextField()),
                ('created_date', models.DateTimeField(verbose_name='Date Created')),
                ('last_modified_date', models.DateTimeField(verbose_name='Date Last Modified')),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('evidence_text', models.TextField()),
                ('impacts_text', models.TextField()),
                ('objectives_text', models.TextField()),
                ('actions_and_outputs_text', models.TextField()),
                ('active_projects_text', models.TextField()),
                ('past_work_text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resource_name', models.CharField(max_length=200)),
                ('resource_url', models.URLField()),
                ('resource_description', models.TextField()),
                ('challenge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rse_challenges_app.challenge')),
            ],
        ),
    ]
