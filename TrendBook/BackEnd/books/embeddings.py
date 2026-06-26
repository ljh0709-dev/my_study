import hashlib
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from django.conf import settings
from django.db import transaction

from .models import BookEmbedding


@dataclass
class EmbeddingSyncResult:
    created: int = 0
    updated: int = 0
    skipped: int = 0


def book_embedding_text(book):
    categories = [link.category.path for link in book.category_links.all()]
    sections = [
        f'제목: {book.title}',
        f'저자: {book.author or "정보 없음"}',
        f'출판사: {book.publisher or "정보 없음"}',
        f'카테고리: {" | ".join(categories) or book.category_name or "정보 없음"}',
        f'도서 소개: {book.description or "소개 없음"}',
    ]
    return '\n'.join(sections)[:8000]


def content_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def cosine_similarity(left, right):
    if len(left) != len(right) or not left:
        raise ValueError('코사인 유사도 벡터 차원이 일치하지 않습니다.')
    dot = sum(float(a) * float(b) for a, b in zip(left, right))
    left_norm = math.sqrt(sum(float(value) ** 2 for value in left))
    right_norm = math.sqrt(sum(float(value) ** 2 for value in right))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


def _embed_chunk(ai_client, chunk):
    response = ai_client.embed([item[1] for item in chunk])
    vectors = response.get('vectors') or []
    dimensions = int(response.get('dimensions') or 0)
    model = str(response.get('model') or '')
    if len(vectors) != len(chunk) or dimensions <= 0 or not model:
        raise ValueError('AI 서비스 임베딩 응답 형식이 올바르지 않습니다.')
    if any(len(vector) != dimensions for vector in vectors):
        raise ValueError('임베딩 벡터 차원이 응답 메타데이터와 다릅니다.')
    return chunk, vectors, dimensions, model


def _save_embedding_chunk(chunk, vectors, dimensions, model, result):
    with transaction.atomic():
        for (book, _, digest, existed), vector in zip(chunk, vectors):
            BookEmbedding.objects.update_or_create(
                book=book,
                defaults={
                    'vector': vector, 'model': model,
                    'dimensions': dimensions, 'content_hash': digest,
                },
            )
            result.updated += int(existed)
            result.created += int(not existed)


def sync_book_embeddings(books, *, ai_client, batch_size=50, force=False, max_workers=1):
    result = EmbeddingSyncResult()
    pending = []
    for book in books:
        text = book_embedding_text(book)
        digest = content_hash(text)
        cached = getattr(book, 'embedding', None)
        if (
            not force and cached and cached.content_hash == digest
            and cached.model == settings.OPENAI_EMBEDDING_MODEL
            and cached.dimensions == settings.OPENAI_EMBEDDING_DIMENSIONS
        ):
            result.skipped += 1
            continue
        pending.append((book, text, digest, bool(cached)))

    chunks = [
        pending[offset:offset + batch_size]
        for offset in range(0, len(pending), batch_size)
    ]
    if max_workers <= 1 or len(chunks) <= 1:
        for chunk in chunks:
            chunk, vectors, dimensions, model = _embed_chunk(ai_client, chunk)
            _save_embedding_chunk(chunk, vectors, dimensions, model, result)
        return result

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_embed_chunk, ai_client, chunk) for chunk in chunks]
        for future in as_completed(futures):
            chunk, vectors, dimensions, model = future.result()
            _save_embedding_chunk(chunk, vectors, dimensions, model, result)
    return result
