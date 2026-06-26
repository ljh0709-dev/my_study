from PIL import Image, ImageDraw, ImageFont


W, H = 3840, 2160
OUT = "output/imagegen/trendbook-erd.png"


def font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE = font(76, True)
SUB = font(34)
GROUP = font(25, True)
HEADER = font(24, True)
FIELD = font(17)
SMALL = font(16)

COLORS = {
    "community": ("#2563eb", "#eff6ff", "#bfdbfe"),
    "book": ("#059669", "#ecfdf5", "#a7f3d0"),
    "trend": ("#d97706", "#fffbeb", "#fde68a"),
    "ai": ("#7c3aed", "#f5f3ff", "#ddd6fe"),
    "ops": ("#475569", "#f8fafc", "#cbd5e1"),
}

entities = {
    "USER": {
        "group": "community",
        "xywh": (80, 260, 520, 310),
        "fields": [
            "bigint id PK",
            "varchar email UK",
            "varchar username",
            "varchar nickname",
            "varchar profile_img",
            "varchar preferred_genres",
            "datetime created_at",
            "datetime updated_at",
        ],
    },
    "BOOK_BOOKMARK": {
        "group": "community",
        "xywh": (80, 640, 520, 165),
        "fields": ["bigint id PK", "bigint user_id FK", "bigint book_id FK", "datetime created_at"],
    },
    "READING_THREAD": {
        "group": "community",
        "xywh": (80, 875, 520, 225),
        "fields": [
            "bigint id PK",
            "bigint author_id FK",
            "bigint book_id FK",
            "varchar title",
            "text content",
            "datetime created_at",
            "datetime updated_at",
        ],
    },
    "THREAD_LIKE": {
        "group": "community",
        "xywh": (80, 1170, 520, 165),
        "fields": ["bigint id PK", "bigint user_id FK", "bigint thread_id FK", "datetime created_at"],
    },
    "THREAD_COMMENT": {
        "group": "community",
        "xywh": (80, 1405, 520, 185),
        "fields": ["bigint id PK", "bigint thread_id FK", "bigint author_id FK", "text content", "datetime created_at"],
    },
    "BOOK": {
        "group": "book",
        "xywh": (720, 260, 640, 555),
        "fields": [
            "bigint id PK",
            "varchar isbn (ISBN13)",
            "varchar isbn10",
            "bigint aladin_item_id UK",
            "varchar mall_type (BOOK | FOREIGN | EBOOK)",
            "varchar title",
            "varchar author",
            "varchar publisher",
            "text description",
            "varchar cover_img",
            "varchar category_name",
            "varchar aladin_link",
            "date pub_date",
            "int price_sales",
            "int price_standard",
            "bigint sales_point",
            "decimal customer_review_rank",
            "varchar stock_status",
            "boolean adult",
            "boolean fixed_price",
            "datetime cached_at",
            "datetime updated_at",
        ],
    },
    "ALADIN_CATEGORY": {
        "group": "book",
        "xywh": (720, 890, 640, 265),
        "fields": [
            "int cid PK",
            "varchar name",
            "varchar mall_type",
            "varchar depth1",
            "varchar depth2",
            "varchar depth3",
            "varchar depth4",
            "varchar depth5",
            "boolean is_active",
        ],
    },
    "BOOK_CATEGORY": {
        "group": "book",
        "xywh": (720, 1230, 300, 170),
        "fields": ["bigint id PK", "bigint book_id FK", "int category_id FK", "boolean is_primary", "datetime created_at"],
    },
    "BOOK_RANKING": {
        "group": "book",
        "xywh": (1060, 1230, 300, 205),
        "fields": ["bigint id PK", "bigint book_id FK", "int category_id FK", "varchar list_type", "int rank", "date period_start", "datetime fetched_at"],
    },
    "BOOK_EMBEDDING": {
        "group": "ai",
        "xywh": (720, 1505, 300, 205),
        "fields": ["bigint id PK", "bigint book_id FK,UK", "json vector", "varchar model", "int dimensions", "varchar content_hash", "datetime embedded_at"],
    },
    "AI_SUMMARY": {
        "group": "ai",
        "xywh": (1060, 1505, 300, 225),
        "fields": ["bigint id PK", "bigint book_id FK,UK", "text sales_reason", "text review_summary", "varchar model", "varchar source_hash", "int review_source_count", "varchar status"],
    },
    "NEWS_ARTICLE": {
        "group": "trend",
        "xywh": (1500, 260, 560, 285),
        "fields": ["bigint id PK", "varchar title", "text summary", "varchar category", "varchar source", "varchar source_url", "varchar cache_key UK", "datetime published_at", "datetime collected_at"],
    },
    "WEATHER_SNAPSHOT": {
        "group": "trend",
        "xywh": (1500, 615, 560, 305),
        "fields": ["bigint id PK", "varchar location", "datetime observed_at", "varchar condition", "float temperature_c", "float feels_like_c", "int humidity", "float wind_speed", "int weather_code", "varchar icon"],
    },
    "TREND_BATCH": {
        "group": "trend",
        "xywh": (2200, 260, 560, 205),
        "fields": ["bigint id PK", "varchar status", "datetime source_started_at", "datetime published_at", "boolean is_legacy", "text error_message"],
    },
    "TREND_TOPIC": {
        "group": "trend",
        "xywh": (2200, 535, 560, 225),
        "fields": ["bigint id PK", "bigint batch_id FK", "varchar title", "text summary", "varchar category", "json keywords", "int rank"],
    },
    "TREND_TOPIC_NEWS": {
        "group": "trend",
        "xywh": (2200, 830, 560, 170),
        "fields": ["bigint id PK", "bigint topic_id FK", "bigint article_id FK", "int rank", "boolean is_primary"],
    },
    "RECOMMENDATION": {
        "group": "trend",
        "xywh": (2960, 260, 560, 245),
        "fields": ["bigint id PK", "bigint topic_id FK", "bigint book_id FK", "text reason", "decimal relevance_score", "decimal retrieval_score", "varchar embedding_model", "datetime created_at"],
    },
    "NEWS_RECOMMENDATION": {
        "group": "trend",
        "xywh": (2960, 575, 560, 245),
        "fields": ["bigint id PK", "bigint topic_news_id FK", "bigint book_id FK", "text reason", "decimal relevance_score", "decimal retrieval_score", "varchar embedding_model", "datetime created_at"],
    },
    "AI_JOB": {
        "group": "ai",
        "xywh": (2960, 890, 560, 305),
        "fields": ["uuid id PK", "varchar kind", "varchar status", "bigint batch_id FK", "bigint topic_id FK", "json request_payload", "text error_message", "datetime created_at", "datetime started_at", "datetime finished_at"],
    },
    "SYNC_RUN": {
        "group": "ops",
        "xywh": (2960, 1265, 560, 225),
        "fields": ["bigint id PK", "varchar lock_key UK", "varchar status", "datetime started_at", "datetime finished_at", "datetime next_run_after", "text error_message", "json metadata"],
    },
}

relations = [
    ("USER", "BOOK_BOOKMARK", "bookmarks"),
    ("USER", "READING_THREAD", "writes"),
    ("USER", "THREAD_LIKE", "likes"),
    ("USER", "THREAD_COMMENT", "comments"),
    ("BOOK", "BOOK_BOOKMARK", "bookmarked_by"),
    ("BOOK", "BOOK_CATEGORY", "classified_as"),
    ("BOOK", "BOOK_RANKING", "ranked"),
    ("BOOK", "READING_THREAD", "reviewed_in"),
    ("BOOK", "RECOMMENDATION", "recommended"),
    ("BOOK", "NEWS_RECOMMENDATION", "recommended_via_news"),
    ("BOOK", "BOOK_EMBEDDING", "embedded 1:1"),
    ("BOOK", "AI_SUMMARY", "analyzed 1:1"),
    ("ALADIN_CATEGORY", "BOOK_CATEGORY", "contains"),
    ("ALADIN_CATEGORY", "BOOK_RANKING", "ranking_scope"),
    ("TREND_BATCH", "TREND_TOPIC", "contains"),
    ("TREND_BATCH", "AI_JOB", "triggers"),
    ("TREND_TOPIC", "TREND_TOPIC_NEWS", "links"),
    ("TREND_TOPIC", "RECOMMENDATION", "produces"),
    ("TREND_TOPIC", "AI_JOB", "triggers"),
    ("NEWS_ARTICLE", "TREND_TOPIC_NEWS", "referenced_by"),
    ("TREND_TOPIC_NEWS", "NEWS_RECOMMENDATION", "produces"),
    ("READING_THREAD", "THREAD_LIKE", "liked"),
    ("READING_THREAD", "THREAD_COMMENT", "commented"),
]


img = Image.new("RGB", (W, H), "#f8fafc")
draw = ImageDraw.Draw(img)

# Subtle background grid
for x in range(0, W, 80):
    draw.line((x, 0, x, H), fill="#eef2f7", width=1)
for y in range(0, H, 80):
    draw.line((0, y, W, y), fill="#eef2f7", width=1)

draw.text((W // 2, 64), "TrendBook ERD", font=TITLE, fill="#0f172a", anchor="mt")
draw.text((W // 2, 152), "README.md Mermaid ERD 기반 데이터 모델", font=SUB, fill="#2563eb", anchor="mt")

legend = [
    ("Accounts / Community", "community"),
    ("Books / Catalog", "book"),
    ("Trends / Recommendations", "trend"),
    ("AI / Jobs", "ai"),
    ("Operations", "ops"),
]
lx = 80
for label, group in legend:
    stroke, fill, _ = COLORS[group]
    draw.rounded_rectangle((lx, 198, lx + 36, 234), radius=8, fill=stroke)
    draw.text((lx + 48, 216), label, font=GROUP, fill="#334155", anchor="lm")
    lx += draw.textlength(label, font=GROUP) + 105


def box_center(name):
    x, y, w, h = entities[name]["xywh"]
    return (x + w / 2, y + h / 2)


def anchor(a, b):
    ax, ay, aw, ah = entities[a]["xywh"]
    bx, by, bw, bh = entities[b]["xywh"]
    acx, acy = ax + aw / 2, ay + ah / 2
    bcx, bcy = bx + bw / 2, by + bh / 2
    if abs(bcx - acx) > abs(bcy - acy):
        p1 = (ax + aw if bcx > acx else ax, acy)
        p2 = (bx if bcx > acx else bx + bw, bcy)
    else:
        p1 = (acx, ay + ah if bcy > acy else ay)
        p2 = (bcx, by if bcy > acy else by + bh)
    return p1, p2


def draw_relation(src, dst, label, idx):
    p1, p2 = anchor(src, dst)
    color = "#64748b"
    width = 3
    x1, y1 = p1
    x2, y2 = p2
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2
    # Orthogonal connector with a small offset pattern to reduce overdraw.
    offset = ((idx % 5) - 2) * 10
    if abs(x2 - x1) > abs(y2 - y1):
        points = [(x1, y1), (mx, y1 + offset), (mx, y2 - offset), (x2, y2)]
    else:
        points = [(x1, y1), (x1 + offset, my), (x2 - offset, my), (x2, y2)]
    draw.line(points, fill=color, width=width, joint="curve")
    # Cardinality hint and compact relation name.
    tx, ty = points[len(points) // 2]
    label_text = f"1:N {label}"
    tw = draw.textlength(label_text, font=SMALL)
    draw.rounded_rectangle((tx - tw / 2 - 8, ty - 13, tx + tw / 2 + 8, ty + 13), radius=7, fill="#ffffff", outline="#cbd5e1")
    draw.text((tx, ty), label_text, font=SMALL, fill="#334155", anchor="mm")


for idx, relation in enumerate(relations):
    draw_relation(*relation, idx)


def draw_table(name, spec):
    x, y, w, h = spec["xywh"]
    stroke, fill, pale = COLORS[spec["group"]]
    # shadow
    draw.rounded_rectangle((x + 6, y + 8, x + w + 6, y + h + 8), radius=18, fill="#dbe3ef")
    draw.rounded_rectangle((x, y, x + w, y + h), radius=18, fill=fill, outline=stroke, width=3)
    draw.rounded_rectangle((x, y, x + w, y + 44), radius=18, fill=stroke)
    draw.rectangle((x, y + 24, x + w, y + 44), fill=stroke)
    draw.text((x + 18, y + 23), name, font=HEADER, fill="#ffffff", anchor="lm")

    yy = y + 60
    for raw in spec["fields"]:
        is_key = " PK" in raw or " FK" in raw or " UK" in raw or "FK," in raw
        bullet = "●" if is_key else "•"
        bullet_color = stroke if is_key else "#94a3b8"
        draw.text((x + 18, yy), bullet, font=FIELD, fill=bullet_color, anchor="lm")
        draw.text((x + 42, yy), raw, font=FIELD, fill="#0f172a", anchor="lm")
        yy += 21


for name, spec in entities.items():
    draw_table(name, spec)

footer_y = 1960
draw.rounded_rectangle((80, footer_y, W - 80, footer_y + 120), radius=24, fill="#ffffff", outline="#cbd5e1", width=2)
draw.text((120, footer_y + 34), "무결성 규칙", font=GROUP, fill="#0f172a", anchor="lm")
rules = [
    "Book.isbn은 ISBN13 우선 저장, (isbn, mall_type) 조합으로 고유성 보장",
    "AladinCategory.cid는 알라딘 CSV CID를 기본키로 사용",
    "BookBookmark(user, book) / Recommendation(topic, book)는 중복 방지",
    "BookEmbedding, AISummary는 Book과 1:1 캐싱 관계",
]
rx = 120
ry = footer_y + 72
for i, rule in enumerate(rules):
    draw.text((rx, ry), f"{i + 1}. {rule}", font=SMALL, fill="#334155", anchor="lm")
    rx += 880

img.save(OUT, "PNG")
print(OUT)
