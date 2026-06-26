from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('trends', '0003_news_weather_topic_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsarticle',
            name='category',
            field=models.CharField(
                choices=[
                    ('TECH_SCIENCE', 'Tech & Science'),
                    ('BUSINESS', 'Business'),
                    ('ARTS_CULTURE', 'Arts & Culture'),
                    ('SPORTS', 'Sports'),
                    ('ENTERTAINMENT', 'Entertainment'),
                ],
                max_length=20,
                verbose_name='수집 분야',
            ),
        ),
        migrations.AlterField(
            model_name='trendtopic',
            name='category',
            field=models.CharField(
                choices=[
                    ('TECH_SCIENCE', 'Tech & Science'),
                    ('BUSINESS', 'Business'),
                    ('ARTS_CULTURE', 'Arts & Culture'),
                    ('SPORTS', 'Sports'),
                    ('ENTERTAINMENT', 'Entertainment'),
                ],
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name='SyncRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lock_key', models.CharField(max_length=80, unique=True)),
                ('status', models.CharField(
                    choices=[
                        ('idle', 'Idle'),
                        ('running', 'Running'),
                        ('completed', 'Completed'),
                        ('failed', 'Failed'),
                        ('skipped', 'Skipped'),
                    ],
                    default='idle',
                    max_length=20,
                )),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('next_run_after', models.DateTimeField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True, default='')),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'sync_run',
                'ordering': ('lock_key',),
            },
        ),
    ]
