from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


def migrate_legacy_recommendations(apps, schema_editor):
    Recommendation = apps.get_model('recommendations', 'Recommendation')
    TrendBatch = apps.get_model('trends', 'TrendBatch')
    TrendTopic = apps.get_model('trends', 'TrendTopic')
    allowed = {'POLITICS', 'ECONOMY', 'TECH', 'CULTURE'}
    cache = {}
    for recommendation in Recommendation.objects.select_related('trend').all():
        trend = recommendation.trend
        topic = cache.get(trend.pk)
        if topic is None:
            batch = TrendBatch.objects.create(
                status='completed', is_legacy=True,
                published_at=trend.created_at, source_started_at=trend.created_at,
            )
            topic = TrendTopic.objects.create(
                batch=batch, title=trend.title, summary=trend.summary,
                category=trend.category if trend.category in allowed else 'CULTURE',
                keywords=[], rank=1,
            )
            cache[trend.pk] = topic
        recommendation.topic = topic
        recommendation.save(update_fields=['topic'])


class Migration(migrations.Migration):
    dependencies = [
        ('recommendations', '0001_initial'),
        ('trends', '0003_news_weather_topic_models'),
        ('books', '0003_alter_book_isbn_book_uq_book_isbn_malltype'),
    ]

    operations = [
        migrations.RenameField(model_name='recommendation', old_name='ai_recommend_reason', new_name='reason'),
        migrations.AlterField(
            model_name='recommendation', name='reason',
            field=models.TextField(verbose_name='추천 사유'),
        ),
        migrations.AddField(
            model_name='recommendation', name='relevance_score',
            field=models.DecimalField(decimal_places=3, default=0.5, max_digits=4, validators=[MinValueValidator(0), MaxValueValidator(1)], verbose_name='관련도'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recommendation', name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recommendations', to='trends.trendtopic', verbose_name='트렌드 주제'),
        ),
        migrations.RunPython(migrate_legacy_recommendations, migrations.RunPython.noop),
        migrations.RemoveConstraint(model_name='recommendation', name='uq_recommendation_trend_book'),
        migrations.RemoveField(model_name='recommendation', name='trend'),
        migrations.AlterField(
            model_name='recommendation', name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommendations', to='trends.trendtopic', verbose_name='트렌드 주제'),
        ),
        migrations.AddConstraint(
            model_name='recommendation',
            constraint=models.UniqueConstraint(fields=('topic', 'book'), name='uq_recommendation_topic_book'),
        ),
        migrations.AlterModelOptions(name='recommendation', options={'ordering': ('-relevance_score', 'id'), 'verbose_name': '추천', 'verbose_name_plural': '추천 목록'}),
    ]
