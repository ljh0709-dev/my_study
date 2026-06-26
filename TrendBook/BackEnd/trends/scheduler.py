import logging
import os
import sys
import threading
import time
from datetime import timedelta

from django.conf import settings
from django.db import close_old_connections
from django.utils import timezone

from .models import SyncRun, TrendBatch
from .services import refresh_discover_cache


logger = logging.getLogger(__name__)
LOCK_KEY = 'discover_refresh'
STALE_RUNNING_AFTER = timedelta(hours=2)
_started = False


def _scheduler_setting_enabled():
    value = str(settings.TRENDBOOK_SCHEDULER_ENABLED).lower()
    if value in {'0', 'false', 'no', 'off'}:
        return False
    if value in {'1', 'true', 'yes', 'on'}:
        return True
    return 'runserver' in sys.argv


def _is_primary_runserver_process():
    if 'runserver' not in sys.argv:
        return False
    return os.environ.get('RUN_MAIN') == 'true' or '--noreload' in sys.argv


def _latest_batch_is_fresh(now):
    latest = TrendBatch.objects.filter(
        status=TrendBatch.Status.COMPLETED,
        is_legacy=False,
    ).order_by('-published_at').first()
    return bool(
        latest and latest.published_at
        and latest.published_at >= now - timedelta(seconds=settings.TREND_REFRESH_INTERVAL_SECONDS)
    )


def run_refresh_if_due(force=False):
    now = timezone.now()
    if not force and _latest_batch_is_fresh(now):
        SyncRun.objects.update_or_create(
            lock_key=LOCK_KEY,
            defaults={
                'status': SyncRun.Status.SKIPPED,
                'finished_at': now,
                'next_run_after': now + timedelta(seconds=settings.TREND_REFRESH_INTERVAL_SECONDS),
                'error_message': '',
                'metadata': {'reason': 'fresh_cache'},
            },
        )
        return False

    run, _ = SyncRun.objects.get_or_create(lock_key=LOCK_KEY)
    stale_cutoff = now - STALE_RUNNING_AFTER
    claimed = SyncRun.objects.filter(pk=run.pk).exclude(
        status=SyncRun.Status.RUNNING,
        started_at__gte=stale_cutoff,
    ).update(
        status=SyncRun.Status.RUNNING,
        started_at=now,
        finished_at=None,
        error_message='',
        metadata={},
    )
    if not claimed:
        return False

    try:
        metadata = refresh_discover_cache()
    except Exception as exc:
        logger.exception('Scheduled Discover refresh failed.')
        SyncRun.objects.filter(pk=run.pk).update(
            status=SyncRun.Status.FAILED,
            finished_at=timezone.now(),
            next_run_after=timezone.now() + timedelta(seconds=settings.TREND_REFRESH_INTERVAL_SECONDS),
            error_message=str(exc)[:2000],
        )
        return False

    SyncRun.objects.filter(pk=run.pk).update(
        status=SyncRun.Status.COMPLETED,
        finished_at=timezone.now(),
        next_run_after=timezone.now() + timedelta(seconds=settings.TREND_REFRESH_INTERVAL_SECONDS),
        error_message='',
        metadata=metadata,
    )
    return True


def _loop():
    while True:
        close_old_connections()
        try:
            try:
                run_refresh_if_due(force=False)
            except Exception:
                logger.exception('Discover refresh scheduler tick failed.')
        finally:
            close_old_connections()
        time.sleep(max(60, int(settings.TREND_REFRESH_INTERVAL_SECONDS)))


def start_scheduler():
    global _started
    if _started or not _scheduler_setting_enabled() or not _is_primary_runserver_process():
        return False
    _started = True
    thread = threading.Thread(target=_loop, name='trendbook-discover-refresh', daemon=True)
    thread.start()
    return True
