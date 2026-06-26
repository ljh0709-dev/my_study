from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    커스텀 사용자 모델 — AbstractUser 확장.
    email을 로그인 ID로 사용하며, 닉네임과 선호 장르를 추가 저장한다.
    """
    email = models.EmailField('이메일', max_length=255, unique=True)
    nickname = models.CharField('닉네임', max_length=50)
    profile_img = models.URLField('프로필 이미지', max_length=500, blank=True, null=True)
    preferred_genres = models.CharField('선호 장르', max_length=255, blank=True, null=True)
    created_at = models.DateTimeField('가입일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nickname']

    class Meta:
        db_table = 'user'
        verbose_name = '사용자'
        verbose_name_plural = '사용자 목록'

    def __str__(self):
        return f'{self.nickname} ({self.email})'
