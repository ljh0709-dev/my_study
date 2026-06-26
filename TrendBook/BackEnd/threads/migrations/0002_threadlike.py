from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('threads', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThreadLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('thread', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='threads.readingthread')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='thread_likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'thread_like',
            },
        ),
        migrations.AddConstraint(
            model_name='threadlike',
            constraint=models.UniqueConstraint(fields=('user', 'thread'), name='uq_thread_like_user_thread'),
        ),
    ]