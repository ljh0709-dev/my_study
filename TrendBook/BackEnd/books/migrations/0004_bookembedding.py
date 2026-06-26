import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('books', '0003_alter_book_isbn_book_uq_book_isbn_malltype')]

    operations = [
        migrations.CreateModel(
            name='BookEmbedding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vector', models.JSONField(verbose_name='임베딩 벡터')),
                ('model', models.CharField(max_length=100, verbose_name='임베딩 모델')),
                ('dimensions', models.PositiveIntegerField(verbose_name='차원')),
                ('content_hash', models.CharField(db_index=True, max_length=64, verbose_name='입력 콘텐츠 해시')),
                ('embedded_at', models.DateTimeField(auto_now=True, verbose_name='생성 시각')),
                ('book', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='embedding', to='books.book', verbose_name='도서')),
            ],
            options={
                'db_table': 'book_embedding',
                'verbose_name': '도서 임베딩',
                'verbose_name_plural': '도서 임베딩 목록',
            },
        ),
    ]
