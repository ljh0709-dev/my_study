import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from books.models import AladinCategory, MallType


DEFAULT_CSV_NAME = 'aladin_Category_CID_20210927 (1).csv'
MALL_TYPE_MAP = {
    '국내도서': MallType.BOOK,
    '외국도서': MallType.FOREIGN,
    '전자책': MallType.EBOOK,
}
REQUIRED_COLUMNS = {'CID', '카테고리명', '몰', '1Depth'}


class Command(BaseCommand):
    help = '알라딘 카테고리 CSV에서 국내도서·외국도서·전자책 CID를 동기화합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=Path,
            default=Path(settings.BASE_DIR).parent / DEFAULT_CSV_NAME,
            help='알라딘 카테고리 CSV 경로',
        )
        parser.add_argument(
            '--deactivate-missing',
            action='store_true',
            help='CSV에 없는 기존 대상 카테고리를 비활성화합니다.',
        )

    def handle(self, *args, **options):
        csv_path = options['path'].expanduser().resolve()
        if not csv_path.is_file():
            raise CommandError(f'CSV 파일을 찾을 수 없습니다: {csv_path}')

        rows, skipped = self._read_rows(csv_path)
        created, updated, unchanged = self._sync_categories(rows)

        deactivated = 0
        if options['deactivate_missing']:
            deactivated = (
                AladinCategory.objects.filter(mall_type__in=MALL_TYPE_MAP.values())
                .exclude(cid__in=rows)
                .filter(is_active=True)
                .update(is_active=False, updated_at=timezone.now())
            )

        self.stdout.write(
            self.style.SUCCESS(
                '알라딘 카테고리 동기화 완료: '
                f'생성 {created}, 수정 {updated}, 동일 {unchanged}, '
                f'제외 {skipped}, 비활성화 {deactivated}'
            )
        )

    def _read_rows(self, csv_path):
        categories = {}
        skipped = 0

        with csv_path.open('r', encoding='utf-8-sig', newline='') as csv_file:
            # 원본 파일의 안내 문구 두 줄 다음에 실제 헤더가 위치한다.
            next(csv_file, None)
            next(csv_file, None)
            reader = csv.DictReader(csv_file)
            missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing_columns:
                raise CommandError(
                    f'필수 컬럼이 없습니다: {", ".join(sorted(missing_columns))}'
                )

            for line_number, row in enumerate(reader, start=4):
                mall_type = MALL_TYPE_MAP.get((row.get('몰') or '').strip())
                if not mall_type:
                    skipped += 1
                    continue

                raw_cid = (row.get('CID') or '').strip()
                try:
                    cid = int(raw_cid)
                except ValueError as exc:
                    raise CommandError(
                        f'{line_number}행 CID가 정수가 아닙니다: {raw_cid!r}'
                    ) from exc

                categories[cid] = {
                    'name': (row.get('카테고리명') or '').strip(),
                    'mall_type': mall_type,
                    'depth1': (row.get('1Depth') or '').strip(),
                    'depth2': (row.get('2Depth') or '').strip(),
                    'depth3': (row.get('3Depth') or '').strip(),
                    'depth4': (row.get('4Depth') or '').strip(),
                    'depth5': (row.get('5Depth') or '').strip(),
                    'is_active': True,
                }

        return categories, skipped

    @transaction.atomic
    def _sync_categories(self, rows):
        existing = AladinCategory.objects.in_bulk(rows)
        now = timezone.now()
        to_create = []
        to_update = []
        unchanged = 0
        update_fields = [
            'name',
            'mall_type',
            'depth1',
            'depth2',
            'depth3',
            'depth4',
            'depth5',
            'is_active',
        ]

        for cid, values in rows.items():
            category = existing.get(cid)
            if category is None:
                to_create.append(
                    AladinCategory(
                        cid=cid,
                        created_at=now,
                        updated_at=now,
                        **values,
                    )
                )
                continue

            changed = False
            for field in update_fields:
                value = values[field]
                if getattr(category, field) != value:
                    setattr(category, field, value)
                    changed = True
            if changed:
                category.updated_at = now
                to_update.append(category)
            else:
                unchanged += 1

        AladinCategory.objects.bulk_create(to_create, batch_size=1000)
        AladinCategory.objects.bulk_update(
            to_update,
            [*update_fields, 'updated_at'],
            batch_size=1000,
        )
        return len(to_create), len(to_update), unchanged
