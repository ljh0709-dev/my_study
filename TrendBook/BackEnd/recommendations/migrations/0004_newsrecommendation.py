import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('books', '0004_bookembedding'),
        ('recommendations', '0003_recommendation_retrieval_provenance'),
        ('trends', '0004_discover_sections_syncrun'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('relevance_score', models.DecimalField(
                    decimal_places=3,
                    max_digits=4,
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(1),
                    ],
                )),
                ('retrieval_score', models.DecimalField(
                    decimal_places=5,
                    default=0,
                    max_digits=6,
                    validators=[
                        django.core.validators.MinValueValidator(-1),
                        django.core.validators.MaxValueValidator(1),
                    ],
                )),
                ('embedding_model', models.CharField(blank=True, default='', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('book', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='news_recommendations',
                    to='books.book',
                )),
                ('topic_news', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='book_recommendations',
                    to='trends.trendtopicnews',
                )),
            ],
            options={
                'db_table': 'news_recommendation',
                'ordering': ('topic_news__rank', '-relevance_score', '-retrieval_score', 'id'),
                'constraints': [
                    models.UniqueConstraint(
                        fields=('topic_news', 'book'),
                        name='uq_news_recommendation_link_book',
                    ),
                ],
            },
        ),
    ]
