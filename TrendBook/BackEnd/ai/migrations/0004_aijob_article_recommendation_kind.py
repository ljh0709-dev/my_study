from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ai', '0003_aisummary_provenance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aijob',
            name='kind',
            field=models.CharField(
                choices=[
                    ('trend', '트렌드 생성'),
                    ('recommendation', '추천 생성'),
                    ('article_recommendation', 'Article recommendation'),
                ],
                max_length=30,
            ),
        ),
    ]
