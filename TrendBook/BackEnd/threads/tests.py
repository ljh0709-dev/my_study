from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from books.models import Book
from .models import Comment, ReadingThread, ThreadLike


class ThreadPermissionTests(APITestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username='owner', email='owner@example.com', nickname='작성자', password='pw')
        self.other = get_user_model().objects.create_user(username='other', email='other@example.com', nickname='다른 사용자', password='pw')
        self.book = Book.objects.create(isbn='9780000000001', title='테스트 도서')

    def test_thread_and_comment_owner_permissions(self):
        self.client.force_authenticate(self.owner)
        created = self.client.post('/api/v1/threads', {'book_isbn': self.book.isbn, 'title': '독후감', 'content': '내용'}, format='json')
        self.assertEqual(created.status_code, 201)
        thread_id = created.data['id']
        comment = self.client.post(f'/api/v1/threads/{thread_id}/comments', {'content': '댓글'}, format='json')
        self.assertEqual(comment.status_code, 201)

        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.patch(f'/api/v1/threads/{thread_id}', {'title': '침범'}, format='json').status_code, 403)
        self.assertEqual(self.client.delete(f"/api/v1/comments/{comment.data['id']}").status_code, 403)

        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.delete(f"/api/v1/comments/{comment.data['id']}").status_code, 204)

    def test_thread_like_create_and_delete(self):
        self.client.force_authenticate(self.owner)
        created = self.client.post(
            '/api/v1/threads',
            {'book_isbn': self.book.isbn, 'title': '리뷰', 'content': '내용'},
            format='json',
        )
        thread_id = created.data['id']

        liked = self.client.post(f'/api/v1/threads/{thread_id}/like')
        self.assertEqual(liked.status_code, 201)
        self.assertEqual(liked.data['like_count'], 1)
        self.assertTrue(liked.data['is_liked'])

        detail = self.client.get(f'/api/v1/threads/{thread_id}')
        self.assertEqual(detail.data['like_count'], 1)
        self.assertTrue(detail.data['is_liked'])

        self.client.force_authenticate(self.other)
        liked_by_other = self.client.post(f'/api/v1/threads/{thread_id}/like')
        self.assertEqual(liked_by_other.data['like_count'], 2)

        unliked = self.client.delete(f'/api/v1/threads/{thread_id}/like')
        self.assertEqual(unliked.status_code, 200)
        self.assertEqual(unliked.data['like_count'], 1)
        self.assertFalse(unliked.data['is_liked'])

    def test_thread_list_includes_like_and_comment_counts(self):
        self.client.force_authenticate(self.owner)
        created = self.client.post(
            '/api/v1/threads',
            {'book_isbn': self.book.isbn, 'title': '리뷰', 'content': '내용'},
            format='json',
        )
        thread_id = created.data['id']
        self.client.post(f'/api/v1/threads/{thread_id}/comments', {'content': '댓글'}, format='json')
        self.client.post(f'/api/v1/threads/{thread_id}/like')

        response = self.client.get('/api/v1/threads', {'book_isbn': self.book.isbn})
        self.assertEqual(response.status_code, 200)
        item = response.data['results'][0]
        self.assertEqual(item['comment_count'], 1)
        self.assertEqual(item['like_count'], 1)

    def test_thread_list_can_filter_my_reviews(self):
        self.client.force_authenticate(self.owner)
        own = self.client.post(
            '/api/v1/threads',
            {'book_isbn': self.book.isbn, 'title': '내 리뷰', 'content': '내용'},
            format='json',
        )
        self.client.force_authenticate(self.other)
        self.client.post(
            '/api/v1/threads',
            {'book_isbn': self.book.isbn, 'title': '다른 리뷰', 'content': '내용'},
            format='json',
        )

        self.client.force_authenticate(self.owner)
        response = self.client.get('/api/v1/threads', {'mine': '1'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], own.data['id'])

    def test_thread_list_supports_ordering(self):
        first = ReadingThread.objects.create(
            author=self.owner,
            book=self.book,
            title='첫 번째 리뷰',
            content='내용',
        )
        second = ReadingThread.objects.create(
            author=self.owner,
            book=self.book,
            title='두 번째 리뷰',
            content='내용',
        )
        third = ReadingThread.objects.create(
            author=self.owner,
            book=self.book,
            title='세 번째 리뷰',
            content='내용',
        )
        Comment.objects.create(author=self.owner, thread=first, content='댓글 1')
        Comment.objects.create(author=self.other, thread=first, content='댓글 2')
        Comment.objects.create(author=self.owner, thread=second, content='댓글 1')
        ThreadLike.objects.create(user=self.owner, thread=second)
        ThreadLike.objects.create(user=self.other, thread=second)
        ThreadLike.objects.create(user=self.owner, thread=third)

        by_likes = self.client.get('/api/v1/threads', {'book_isbn': self.book.isbn, 'ordering': 'likes'})
        self.assertEqual(by_likes.status_code, 200)
        self.assertEqual(by_likes.data['results'][0]['id'], second.id)

        by_comments = self.client.get('/api/v1/threads', {'book_isbn': self.book.isbn, 'ordering': 'comments'})
        self.assertEqual(by_comments.status_code, 200)
        self.assertEqual(by_comments.data['results'][0]['id'], first.id)

        fallback = self.client.get('/api/v1/threads', {'book_isbn': self.book.isbn, 'ordering': 'unknown'})
        self.assertEqual(fallback.status_code, 200)
        self.assertEqual(fallback.data['results'][0]['id'], third.id)

    def test_thread_list_supports_search(self):
        other_book = Book.objects.create(
            isbn='9780000000002',
            title='Python Testing Guide',
            author='Ada Writer',
        )
        matching_title = ReadingThread.objects.create(
            author=self.owner,
            book=self.book,
            title='깊은 독서 메모',
            content='평범한 내용',
        )
        matching_content = ReadingThread.objects.create(
            author=self.other,
            book=self.book,
            title='다른 리뷰',
            content='검색어가 본문에 있습니다',
        )
        matching_book = ReadingThread.objects.create(
            author=self.owner,
            book=other_book,
            title='기술책 리뷰',
            content='테스트 자동화',
        )
        ReadingThread.objects.create(
            author=self.owner,
            book=self.book,
            title='관련 없는 글',
            content='다른 내용',
        )

        by_title = self.client.get('/api/v1/threads', {'q': '깊은'})
        self.assertEqual(by_title.status_code, 200)
        self.assertEqual(by_title.data['count'], 1)
        self.assertEqual(by_title.data['results'][0]['id'], matching_title.id)

        by_content = self.client.get('/api/v1/threads', {'q': '검색어'})
        self.assertEqual(by_content.data['count'], 1)
        self.assertEqual(by_content.data['results'][0]['id'], matching_content.id)

        by_book = self.client.get('/api/v1/threads', {'q': 'Python'})
        self.assertEqual(by_book.data['count'], 1)
        self.assertEqual(by_book.data['results'][0]['id'], matching_book.id)
