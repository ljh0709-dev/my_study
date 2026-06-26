from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book, BookBookmark
from threads.models import ReadingThread

from .models import User


@override_settings(
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
    SECRET_KEY='trendbook-test-secret-key-at-least-thirty-two-characters',
)
class AuthenticationAPITests(APITestCase):
    register_payload = {
        'email': 'reader@example.com',
        'nickname': '리더',
        'password': 'TrendBook123!',
        'password_confirm': 'TrendBook123!',
    }

    def test_register_login_refresh_and_profile_flow(self):
        register_response = self.client.post(
            reverse('accounts:register'),
            self.register_payload,
            format='json',
        )
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', register_response.data)
        self.assertEqual(User.objects.get().email, 'reader@example.com')

        login_response = self.client.post(
            reverse('accounts:login'),
            {'email': 'reader@example.com', 'password': 'TrendBook123!'},
            format='json',
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)
        self.assertEqual(login_response.data['user']['nickname'], '리더')

        refresh_response = self.client.post(
            reverse('accounts:token-refresh'),
            {'refresh': login_response.data['refresh']},
            format='json',
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
        profile_response = self.client.patch(
            reverse('accounts:me'),
            {'nickname': '새 닉네임', 'preferred_genres': '소설,과학'},
            format='json',
        )
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['nickname'], '새 닉네임')

    def test_duplicate_email_and_password_mismatch_are_rejected(self):
        User.objects.create_user(
            username='existing',
            email='reader@example.com',
            nickname='기존 사용자',
            password='TrendBook123!',
        )
        duplicate = self.client.post(
            reverse('accounts:register'),
            self.register_payload,
            format='json',
        )
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)

        mismatch_payload = {
            **self.register_payload,
            'email': 'new@example.com',
            'password_confirm': 'Different123!',
        }
        mismatch = self.client.post(
            reverse('accounts:register'),
            mismatch_payload,
            format='json',
        )
        self.assertEqual(mismatch.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse('accounts:me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_delete_own_account(self):
        user = User.objects.create_user(
            username='delete_me',
            email='delete@example.com',
            nickname='탈퇴 사용자',
            password='TrendBook123!',
        )
        book = Book.objects.create(isbn='9780000000999', title='탈퇴 테스트 도서')
        BookBookmark.objects.create(user=user, book=book)
        ReadingThread.objects.create(
            author=user,
            book=book,
            title='내 리뷰',
            content='탈퇴 전 리뷰',
        )

        login_response = self.client.post(
            reverse('accounts:login'),
            {'email': 'delete@example.com', 'password': 'TrendBook123!'},
            format='json',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")

        delete_response = self.client.delete(reverse('accounts:me'))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(email='delete@example.com').exists())
        self.assertFalse(BookBookmark.objects.filter(user_id=user.id).exists())
        self.assertFalse(ReadingThread.objects.filter(author_id=user.id).exists())

        self.client.credentials()
        profile_response = self.client.get(reverse('accounts:me'))
        self.assertEqual(profile_response.status_code, status.HTTP_401_UNAUTHORIZED)


class HealthAPITests(APITestCase):
    def test_health_endpoint(self):
        response = self.client.get(
            reverse('health'),
            HTTP_ORIGIN='http://localhost:5173',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(
            response.headers['Access-Control-Allow-Origin'],
            'http://localhost:5173',
        )
