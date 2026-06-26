import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('ai', '0001_initial'), ('trends', '0003_news_weather_topic_models')]

    operations = [
        migrations.CreateModel(
            name='AIJob',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('kind', models.CharField(choices=[('trend', '트렌드 생성'), ('recommendation', '추천 생성')], max_length=20)),
                ('status', models.CharField(choices=[('pending', '대기'), ('processing', '처리 중'), ('completed', '완료'), ('failed', '실패')], default='pending', max_length=20)),
                ('request_payload', models.JSONField(blank=True, default=dict)),
                ('error_message', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('batch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ai_jobs', to='trends.trendbatch')),
                ('topic', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ai_jobs', to='trends.trendtopic')),
            ],
            options={
                'db_table': 'ai_job',
                'ordering': ('-created_at',),
                'constraints': [
                    models.UniqueConstraint(condition=models.Q(('kind', 'recommendation'), ('status__in', ['pending', 'processing']), ('topic__isnull', False)), fields=('topic',), name='uq_active_recommendation_job'),
                ],
            },
        ),
    ]
