from django.conf import settings

MIN_RECOMMENDATION_SALES_POINT = int(
    getattr(settings, 'MIN_RECOMMENDATION_SALES_POINT', 1000),
)
MAX_TOPIC_RECOMMENDATIONS = 5


def book_meets_recommendation_threshold(book):
    return (book.sales_point or 0) >= MIN_RECOMMENDATION_SALES_POINT


def filter_recommendation_records(records, *, limit=MAX_TOPIC_RECOMMENDATIONS):
    seen_isbns = set()
    filtered = []
    for record in records:
        book = getattr(record, 'book', None)
        if not book or not book.isbn:
            continue
        if book.isbn in seen_isbns:
            continue
        if not book_meets_recommendation_threshold(book):
            continue
        seen_isbns.add(book.isbn)
        filtered.append(record)
        if len(filtered) >= limit:
            break
    return filtered