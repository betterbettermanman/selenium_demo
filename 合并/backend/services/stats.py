from datetime import date, datetime, timedelta

from sqlalchemy import case, func

from models import db
from models.task import Task
from models.website import Website


def _int(value):
    return int(value or 0)


def _range_bounds(start_date, end_date):
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
    return start_dt, end_dt


def _in_range(query, start_date, end_date):
    start_dt, end_dt = _range_bounds(start_date, end_date)
    return query.filter(
        Task.create_time.isnot(None),
        Task.create_time >= start_dt,
        Task.create_time < end_dt,
    )


def _charged_expr():
    return case((Task.is_charged == '1', 1), else_=0)


def _free_expr():
    return case((Task.is_charged == '1', 0), else_=1)


def _completed_expr():
    return case((Task.status == '2', 1), else_=0)


def _pending_expr():
    return case((Task.status == '2', 0), else_=1)


def _revenue_expr():
    """接单金额：与接单数量同一批任务的 price 之和，不区分是否收费。"""
    return func.coalesce(Task.price, 0)


def _summarize(query):
    row = query.with_entities(
        func.count(Task.id).label('order_count'),
        func.coalesce(func.sum(_charged_expr()), 0).label('charged_count'),
        func.coalesce(func.sum(_free_expr()), 0).label('free_count'),
        func.coalesce(func.sum(_revenue_expr()), 0).label('revenue'),
    ).one()
    return {
        'order_count': _int(row.order_count),
        'charged_count': _int(row.charged_count),
        'free_count': _int(row.free_count),
        'revenue': _int(row.revenue),
    }


def _today_summary():
    today = date.today()
    data = _summarize(_in_range(db.session.query(Task), today, today))
    return {'order_count': data['order_count'], 'revenue': data['revenue']}


def _total_summary():
    data = _summarize(db.session.query(Task))
    return {'order_count': data['order_count'], 'revenue': data['revenue']}


def _range_summary(start_date, end_date):
    return _summarize(_in_range(db.session.query(Task), start_date, end_date))


def _daily_rows(start_date, end_date):
    day_col = func.date(Task.create_time)
    rows = (
        _in_range(db.session.query(Task), start_date, end_date)
        .with_entities(
            day_col.label('day'),
            func.count(Task.id).label('order_count'),
            func.coalesce(func.sum(_charged_expr()), 0).label('charged_count'),
            func.coalesce(func.sum(_free_expr()), 0).label('free_count'),
            func.coalesce(func.sum(_revenue_expr()), 0).label('revenue'),
            func.coalesce(func.sum(_completed_expr()), 0).label('completed_count'),
            func.coalesce(func.sum(_pending_expr()), 0).label('pending_count'),
        )
        .group_by(day_col)
        .order_by(day_col.desc())
        .all()
    )
    result = []
    for row in rows:
        result.append(
            {
                'date': str(row.day)[:10],
                'order_count': _int(row.order_count),
                'charged_count': _int(row.charged_count),
                'free_count': _int(row.free_count),
                'revenue': _int(row.revenue),
                'completed_count': _int(row.completed_count),
                'pending_count': _int(row.pending_count),
            }
        )
    return result


def _website_totals():
    site_code = func.coalesce(Task.website_code, '')
    rows = (
        db.session.query(
            site_code.label('website_code'),
            func.count(Task.id).label('order_count'),
            func.coalesce(func.sum(_revenue_expr()), 0).label('revenue'),
        )
        .group_by(site_code)
        .all()
    )
    return {
        row.website_code: {
            'total_order_count': _int(row.order_count),
            'total_revenue': _int(row.revenue),
        }
        for row in rows
    }


def _by_website_rows(start_date, end_date, range_revenue):
    site_code = func.coalesce(Task.website_code, '')
    rows = (
        _in_range(db.session.query(Task), start_date, end_date)
        .outerjoin(Website, Task.website_code == Website.code)
        .with_entities(
            site_code.label('website_code'),
            func.max(Website.name).label('website_name'),
            func.count(Task.id).label('order_count'),
            func.coalesce(func.sum(_charged_expr()), 0).label('charged_count'),
            func.coalesce(func.sum(_revenue_expr()), 0).label('revenue'),
        )
        .group_by(site_code)
        .all()
    )
    totals = _website_totals()
    result = []
    for row in rows:
        revenue = _int(row.revenue)
        code = row.website_code or ''
        total = totals.get(code, {'total_order_count': 0, 'total_revenue': 0})
        result.append(
            {
                'website_code': code,
                'website_name': row.website_name or '',
                'order_count': _int(row.order_count),
                'charged_count': _int(row.charged_count),
                'revenue': revenue,
                'revenue_share': round(revenue / range_revenue, 4) if range_revenue else 0,
                'total_order_count': total['total_order_count'],
                'total_revenue': total['total_revenue'],
            }
        )
    result.sort(key=lambda item: (-item['revenue'], -item['order_count'], item['website_code']))
    return result


def build_overview(start_date, end_date):
    range_data = _range_summary(start_date, end_date)
    return {
        'today': _today_summary(),
        'total': _total_summary(),
        'range': range_data,
        'daily': _daily_rows(start_date, end_date),
        'by_website': _by_website_rows(start_date, end_date, range_data['revenue']),
    }
