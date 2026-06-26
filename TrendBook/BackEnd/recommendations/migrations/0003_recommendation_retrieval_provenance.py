from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('recommendations', '0002_topic_recommendations')]

    operations = [
        migrations.AddField(
            model_name='recommendation', name='embedding_model',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='임베딩 모델'),
        ),
        migrations.AddField(
            model_name='recommendation', name='retrieval_score',
            field=models.DecimalField(decimal_places=5, default=0, max_digits=6, validators=[MinValueValidator(-1), MaxValueValidator(1)], verbose_name='벡터 검색 유사도'),
        ),
        migrations.AlterModelOptions(
            name='recommendation',
            options={'ordering': ('-relevance_score', '-retrieval_score', 'id'), 'verbose_name': '추천', 'verbose_name_plural': '추천 목록'},
        ),
    ]
