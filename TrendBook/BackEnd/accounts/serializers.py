from uuid import uuid4

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'nickname',
            'profile_img',
            'preferred_genres',
            'created_at',
        )
        read_only_fields = ('id', 'email', 'username', 'created_at')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ('email', 'nickname', 'password', 'password_confirm')

    def validate_email(self, value):
        email = User.objects.normalize_email(value).lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('이미 사용 중인 이메일입니다.')
        return email

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '비밀번호가 일치하지 않습니다.'})
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(
            username=f'user_{uuid4().hex}',
            **validated_data,
        )
        user.set_password(password)
        user.save()
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['nickname'] = user.nickname
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data

