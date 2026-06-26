from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('ai', '0002_aijob')]

    operations = [
        migrations.AddField(
            model_name='aisummary', name='model',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='생성 모델'),
        ),
        migrations.AddField(
            model_name='aisummary', name='review_source_count',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='리뷰 발췌 수'),
        ),
        migrations.AddField(
            model_name='aisummary', name='source_hash',
            field=models.CharField(blank=True, db_index=True, default='', max_length=64, verbose_name='입력 데이터 해시'),
        ),
    ]
