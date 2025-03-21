# Generated by Django 5.1.3 on 2024-12-08 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rse_challenges_app', '0002_rename_challenge_description_challenge_description_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('status', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Evidence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='challenge',
            name='actions_and_outputs_text',
        ),
        migrations.RemoveField(
            model_name='challenge',
            name='active_projects_text',
        ),
        migrations.RemoveField(
            model_name='challenge',
            name='evidence_text',
        ),
        migrations.RemoveField(
            model_name='challenge',
            name='impacts_text',
        ),
        migrations.RemoveField(
            model_name='challenge',
            name='objectives_text',
        ),
        migrations.RemoveField(
            model_name='challenge',
            name='past_work_text',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='challenge',
        ),
        migrations.AddField(
            model_name='challenge',
            name='resources',
            field=models.ManyToManyField(to='rse_challenges_app.resource'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='actions',
            field=models.ManyToManyField(to='rse_challenges_app.action'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='evidences',
            field=models.ManyToManyField(to='rse_challenges_app.evidence'),
        ),
        migrations.CreateModel(
            name='Impact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('evidences', models.ManyToManyField(to='rse_challenges_app.evidence')),
            ],
        ),
        migrations.AddField(
            model_name='challenge',
            name='impacts',
            field=models.ManyToManyField(to='rse_challenges_app.impact'),
        ),
        migrations.CreateModel(
            name='Input',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('actions', models.ManyToManyField(to='rse_challenges_app.action')),
            ],
        ),
        migrations.AddField(
            model_name='challenge',
            name='inputs',
            field=models.ManyToManyField(to='rse_challenges_app.input'),
        ),
        migrations.CreateModel(
            name='Objective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('impacts', models.ManyToManyField(to='rse_challenges_app.impact')),
            ],
        ),
        migrations.AddField(
            model_name='challenge',
            name='objectives',
            field=models.ManyToManyField(to='rse_challenges_app.objective'),
        ),
        migrations.CreateModel(
            name='Output',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('objectives', models.ManyToManyField(to='rse_challenges_app.objective')),
            ],
        ),
        migrations.AddField(
            model_name='action',
            name='outputs',
            field=models.ManyToManyField(to='rse_challenges_app.output'),
        ),
        migrations.AddField(
            model_name='challenge',
            name='outputs',
            field=models.ManyToManyField(to='rse_challenges_app.output'),
        ),
    ]
