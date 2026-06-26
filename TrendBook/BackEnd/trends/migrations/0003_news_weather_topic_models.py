import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('trends', '0002_trendissue_cache_key_trendissue_metadata_and_more')]

    operations = [
        migrations.CreateModel(
            name='NewsArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500, verbose_name='기사 제목')),
                ('summary', models.TextField(blank=True, default='', verbose_name='기사 요약')),
                ('category', models.CharField(choices=[('POLITICS', '정치'), ('ECONOMY', '경제'), ('SOCIETY', '사회'), ('TECH', '기술'), ('CULTURE', '문화'), ('WORLD', '국제')], max_length=20, verbose_name='수집 분야')),
                ('source', models.CharField(blank=True, default='', max_length=150, verbose_name='언론사/제공자')),
                ('source_url', models.URLField(max_length=1000, verbose_name='원문 URL')),
                ('cache_key', models.CharField(max_length=64, unique=True, verbose_name='원문 URL 해시')),
                ('published_at', models.DateTimeField(db_index=True, verbose_name='원문 발행 시각')),
                ('collected_at', models.DateTimeField(auto_now_add=True, verbose_name='수집 시각')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='갱신 시각')),
            ],
            options={'db_table': 'news_article', 'ordering': ('-published_at', '-id')},
        ),
        migrations.CreateModel(
            name='TrendBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', '대기'), ('processing', '처리 중'), ('completed', '완료'), ('failed', '실패')], default='pending', max_length=20)),
                ('source_started_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('published_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('is_legacy', models.BooleanField(db_index=True, default=False)),
                ('error_message', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'trend_batch', 'ordering': ('-published_at', '-created_at')},
        ),
        migrations.CreateModel(
            name='WeatherSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=100, verbose_name='위치')),
                ('observed_at', models.DateTimeField(verbose_name='관측 기준 시각')),
                ('condition', models.CharField(blank=True, default='', max_length=100, verbose_name='날씨')),
                ('temperature_c', models.FloatField(blank=True, null=True, verbose_name='기온')),
                ('feels_like_c', models.FloatField(blank=True, null=True, verbose_name='체감 기온')),
                ('humidity', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='습도')),
                ('wind_speed', models.FloatField(blank=True, null=True, verbose_name='풍속')),
                ('weather_code', models.IntegerField(blank=True, null=True, verbose_name='날씨 코드')),
                ('icon', models.CharField(blank=True, default='', max_length=20, verbose_name='아이콘')),
                ('collected_at', models.DateTimeField(auto_now_add=True, verbose_name='수집 시각')),
            ],
            options={
                'db_table': 'weather_snapshot',
                'ordering': ('-observed_at', '-id'),
                'constraints': [models.UniqueConstraint(fields=('location', 'observed_at'), name='uq_weather_location_observed')],
            },
        ),
        migrations.CreateModel(
            name='TrendTopic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('summary', models.TextField()),
                ('category', models.CharField(choices=[('POLITICS', '정치'), ('ECONOMY', '경제'), ('SOCIETY', '사회'), ('TECH', '기술'), ('CULTURE', '문화'), ('WORLD', '국제')], max_length=20)),
                ('keywords', models.JSONField(blank=True, default=list)),
                ('rank', models.PositiveSmallIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='trends.trendbatch')),
            ],
            options={
                'db_table': 'trend_topic',
                'ordering': ('rank', 'id'),
                'constraints': [
                    models.UniqueConstraint(fields=('batch', 'rank'), name='uq_topic_batch_rank'),
                    models.CheckConstraint(condition=models.Q(('rank__gte', 1), ('rank__lte', 5)), name='ck_topic_rank'),
                ],
            },
        ),
        migrations.CreateModel(
            name='TrendTopicNews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.PositiveSmallIntegerField()),
                ('is_primary', models.BooleanField(default=False)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topic_links', to='trends.newsarticle')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_links', to='trends.trendtopic')),
            ],
            options={
                'db_table': 'trend_topic_news',
                'ordering': ('rank', 'id'),
                'constraints': [
                    models.UniqueConstraint(fields=('topic', 'article'), name='uq_topic_article'),
                    models.UniqueConstraint(fields=('topic', 'rank'), name='uq_topic_article_rank'),
                    models.UniqueConstraint(condition=models.Q(('is_primary', True)), fields=('topic',), name='uq_topic_primary_article'),
                    models.CheckConstraint(condition=models.Q(('rank__gte', 1), ('rank__lte', 5)), name='ck_topic_article_rank'),
                ],
            },
        ),
        migrations.AddField(
            model_name='trendtopic', name='articles',
            field=models.ManyToManyField(blank=True, related_name='topics', through='trends.TrendTopicNews', to='trends.newsarticle'),
        ),
        migrations.AddIndex(
            model_name='newsarticle',
            index=models.Index(fields=['category', '-published_at'], name='idx_news_category_pub'),
        ),
        migrations.AlterModelOptions(
            name='trendissue',
            options={'verbose_name': '레거시 트렌드 이슈', 'verbose_name_plural': '레거시 트렌드 이슈 목록'},
        ),
    ]
