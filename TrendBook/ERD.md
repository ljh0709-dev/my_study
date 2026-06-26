# TrendBook ERD

알라딘의 국내도서(`BOOK`), 외국도서(`FOREIGN`), 전자책(`EBOOK`)을 공통 도서 구조로 관리한다. 카테고리 CID는 몰 전체에서 고유하며, 하나의 도서는 여러 카테고리에 속할 수 있다.

```mermaid
erDiagram
    USER ||--o{ BOOK_BOOKMARK : bookmarks
    USER ||--o{ READING_THREAD : writes
    USER ||--o{ THREAD_LIKE : likes
    USER ||--o{ THREAD_COMMENT : comments
    BOOK ||--o{ BOOK_BOOKMARK : bookmarked_by
    BOOK ||--o{ BOOK_CATEGORY : classified_as
    BOOK ||--o{ BOOK_RANKING : ranked
    BOOK ||--o{ READING_THREAD : reviewed_in
    BOOK ||--o{ RECOMMENDATION : recommended
    BOOK ||--o{ NEWS_RECOMMENDATION : recommended_via_news
    BOOK ||--o| BOOK_EMBEDDING : embedded
    BOOK ||--o| AI_SUMMARY : analyzed
    ALADIN_CATEGORY ||--o{ BOOK_CATEGORY : contains
    ALADIN_CATEGORY o|--o{ BOOK_RANKING : ranking_scope
    TREND_BATCH ||--o{ TREND_TOPIC : contains
    TREND_BATCH ||--o{ AI_JOB : triggers
    TREND_TOPIC ||--o{ TREND_TOPIC_NEWS : links
    TREND_TOPIC ||--o{ RECOMMENDATION : produces
    TREND_TOPIC ||--o{ AI_JOB : triggers
    NEWS_ARTICLE ||--o{ TREND_TOPIC_NEWS : referenced_by
    TREND_TOPIC_NEWS ||--o{ NEWS_RECOMMENDATION : produces
    READING_THREAD ||--o{ THREAD_LIKE : liked
    READING_THREAD ||--o{ THREAD_COMMENT : commented

    USER {
        bigint id PK
        varchar email UK
        varchar username
        varchar nickname
        varchar profile_img
        varchar preferred_genres
        datetime created_at
        datetime updated_at
    }

    BOOK {
        bigint id PK
        varchar isbn "ISBN13"
        varchar isbn10
        bigint aladin_item_id UK
        varchar mall_type "BOOK | FOREIGN | EBOOK"
        varchar title
        varchar author
        varchar publisher
        text description
        varchar cover_img
        varchar category_name
        varchar aladin_link
        date pub_date
        int price_sales
        int price_standard
        bigint sales_point
        decimal customer_review_rank
        varchar stock_status
        boolean adult
        boolean fixed_price
        datetime cached_at
        datetime updated_at
    }

    ALADIN_CATEGORY {
        int cid PK
        varchar name
        varchar mall_type
        varchar depth1
        varchar depth2
        varchar depth3
        varchar depth4
        varchar depth5
        boolean is_active
    }

    BOOK_CATEGORY {
        bigint id PK
        bigint book_id FK
        int category_id FK
        boolean is_primary
        datetime created_at
    }

    BOOK_RANKING {
        bigint id PK
        bigint book_id FK
        int category_id FK "nullable"
        varchar list_type "BESTSELLER | ITEM_NEW_ALL | ..."
        int rank
        date period_start
        datetime fetched_at
    }

    BOOK_BOOKMARK {
        bigint id PK
        bigint user_id FK
        bigint book_id FK
        datetime created_at
    }

    BOOK_EMBEDDING {
        bigint id PK
        bigint book_id FK,UK
        json vector
        varchar model
        int dimensions
        varchar content_hash
        datetime embedded_at
    }

    NEWS_ARTICLE {
        bigint id PK
        varchar title
        text summary
        varchar category
        varchar source
        varchar source_url
        varchar cache_key UK
        datetime published_at
        datetime collected_at
    }

    WEATHER_SNAPSHOT {
        bigint id PK
        varchar location
        datetime observed_at
        varchar condition
        float temperature_c
        float feels_like_c
        int humidity
        float wind_speed
        int weather_code
        varchar icon
    }

    TREND_BATCH {
        bigint id PK
        varchar status
        datetime source_started_at
        datetime published_at
        boolean is_legacy
        text error_message
    }

    TREND_TOPIC {
        bigint id PK
        bigint batch_id FK
        varchar title
        text summary
        varchar category
        json keywords
        int rank
    }

    TREND_TOPIC_NEWS {
        bigint id PK
        bigint topic_id FK
        bigint article_id FK
        int rank
        boolean is_primary
    }

    RECOMMENDATION {
        bigint id PK
        bigint topic_id FK
        bigint book_id FK
        text reason
        decimal relevance_score
        decimal retrieval_score
        varchar embedding_model
        datetime created_at
    }

    NEWS_RECOMMENDATION {
        bigint id PK
        bigint topic_news_id FK
        bigint book_id FK
        text reason
        decimal relevance_score
        decimal retrieval_score
        varchar embedding_model
        datetime created_at
    }

    AI_SUMMARY {
        bigint id PK
        bigint book_id FK,UK
        text sales_reason
        text review_summary
        varchar model
        varchar source_hash
        int review_source_count
        varchar status
    }

    AI_JOB {
        uuid id PK
        varchar kind "trend | recommendation | article_recommendation"
        varchar status "pending | processing | completed | failed"
        bigint batch_id FK
        bigint topic_id FK
        json request_payload
        text error_message
        datetime created_at
        datetime started_at
        datetime finished_at
    }

    READING_THREAD {
        bigint id PK
        bigint author_id FK
        bigint book_id FK
        varchar title
        text content
        datetime created_at
        datetime updated_at
    }

    THREAD_LIKE {
        bigint id PK
        bigint user_id FK
        bigint thread_id FK
        datetime created_at
    }

    THREAD_COMMENT {
        bigint id PK
        bigint thread_id FK
        bigint author_id FK
        text content
        datetime created_at
    }

    SYNC_RUN {
        bigint id PK
        varchar lock_key UK
        varchar status
        datetime started_at
        datetime finished_at
        datetime next_run_after
        text error_message
        json metadata
    }
```

## 무결성 규칙

- `Book.isbn`은 ISBN13을 우선 저장하고 고유하게 관리한다.
- `AladinCategory.cid`는 CSV의 CID를 그대로 기본키로 사용한다.
- `BookCategory(book, category)` 조합은 중복될 수 없다.
- 한 도서에는 `is_primary=true`인 대표 카테고리를 최대 하나만 둔다.
- 동일 도서·리스트 유형·집계일·카테고리 범위의 순위는 하나만 저장한다.
- 카테고리 CSV에 부모 CID가 없으므로 임의의 자기참조 FK를 만들지 않고 `depth1`~`depth5` 원형을 보존한다.
