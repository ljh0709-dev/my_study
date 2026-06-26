import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ('books', '0003_alter_book_isbn_book_uq_book_isbn_malltype')]
    operations = [
        migrations.CreateModel(
            name='ReadingThread',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reading_threads', to=settings.AUTH_USER_MODEL)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reading_threads', to='books.book')),
            ],
            options={'db_table': 'reading_thread', 'ordering': ('-created_at',)},
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='thread_comments', to=settings.AUTH_USER_MODEL)),
                ('thread', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='threads.readingthread')),
            ],
            options={'db_table': 'thread_comment', 'ordering': ('created_at',)},
        ),
    ]
