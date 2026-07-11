import logging
import os
import threading
import time
from contextlib import contextmanager
from urllib.parse import urlparse

from flask import request
from sqlalchemy import event

perf_logger = logging.getLogger('api.perf')
db_perf_logger = logging.getLogger('db.perf')

_request_stats = threading.local()
_registered_engines = set()


def get_db_endpoint(database_uri: str) -> str:
    normalized = database_uri.replace('mysql+pymysql://', 'mysql://', 1)
    parsed = urlparse(normalized)
    host = parsed.hostname or 'unknown'
    port = parsed.port or 3306
    database = (parsed.path or '').lstrip('/') or 'unknown'
    return f'{host}:{port}/{database}'


def reset_request_stats():
    _request_stats.queries = []
    _request_stats.start = time.perf_counter()
    _request_stats.phases = []


def add_query_stat(duration_ms: float, statement: str):
    if not hasattr(_request_stats, 'queries'):
        _request_stats.queries = []
    _request_stats.queries.append({
        'ms': round(duration_ms, 1),
        'stmt': ' '.join(statement.split())[:500],
    })


def add_phase_stat(phase: str, duration_ms: float, **extra):
    if not hasattr(_request_stats, 'phases'):
        _request_stats.phases = []
    _request_stats.phases.append({
        'phase': phase,
        'ms': round(duration_ms, 1),
        **extra,
    })


def get_request_stats():
    queries = getattr(_request_stats, 'queries', [])
    return {
        'count': len(queries),
        'total_ms': round(sum(q['ms'] for q in queries), 1),
        'queries': queries,
        'phases': getattr(_request_stats, 'phases', []),
    }


def _register_engine_events(engine, slow_sql_ms: float):
    if id(engine) in _registered_engines:
        return

    @event.listens_for(engine, 'before_cursor_execute')
    def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.perf_counter())

    @event.listens_for(engine, 'after_cursor_execute')
    def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        starts = conn.info.get('query_start_time', [])
        if not starts:
            return
        start = starts.pop()
        duration_ms = (time.perf_counter() - start) * 1000
        stmt = ' '.join(statement.split())
        add_query_stat(duration_ms, stmt)
        if duration_ms >= slow_sql_ms:
            db_perf_logger.warning('SLOW SQL %.1fms | %s', duration_ms, stmt[:500])
        else:
            db_perf_logger.debug('SQL %.1fms | %s', duration_ms, stmt[:200])

    _registered_engines.add(id(engine))


def setup_perf_logging(app, database_uri: str):
    db_endpoint = get_db_endpoint(database_uri)
    slow_sql_ms = float(os.getenv('DB_SLOW_SQL_MS', '100'))
    slow_api_ms = float(os.getenv('API_SLOW_REQUEST_MS', '500'))

    perf_logger.setLevel(logging.INFO)
    db_perf_logger.setLevel(logging.INFO)
    perf_logger.info(
        '性能日志已启用 | db=%s | slow_sql=%sms slow_api=%sms',
        db_endpoint, slow_sql_ms, slow_api_ms,
    )

    with app.app_context():
        from models import db
        _register_engine_events(db.engine, slow_sql_ms)

    @app.before_request
    def _perf_request_start():
        if request.path.startswith('/api/'):
            reset_request_stats()

    @app.after_request
    def _perf_request_end(response):
        if not request.path.startswith('/api/'):
            return response
        if not hasattr(_request_stats, 'start'):
            return response

        total_ms = (time.perf_counter() - _request_stats.start) * 1000
        stats = get_request_stats()
        phase_text = ' '.join(
            f"{p['phase']}={p['ms']}ms" for p in stats.get('phases', [])
        )
        query_args = request.query_string.decode('utf-8', errors='ignore')
        base_msg = (
            f'{request.method} {request.path}'
            f'{"?" + query_args if query_args else ""} | '
            f'total={total_ms:.1f}ms db={db_endpoint} '
            f'db_queries={stats["count"]} db_sql_total={stats["total_ms"]:.1f}ms'
        )
        if phase_text:
            base_msg += f' | {phase_text}'

        if total_ms >= slow_api_ms:
            perf_logger.warning('SLOW API | %s', base_msg)
            for query in stats['queries']:
                perf_logger.warning('  SQL %.1fms | %s', query['ms'], query['stmt'])
        else:
            perf_logger.info(base_msg)

        return response

    return db_endpoint


@contextmanager
def track_phase(phase: str, **extra):
    start = time.perf_counter()
    try:
        yield
    finally:
        add_phase_stat(phase, (time.perf_counter() - start) * 1000, **extra)
