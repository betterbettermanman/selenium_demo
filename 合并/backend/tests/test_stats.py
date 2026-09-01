"""接单统计接口：按创建日聚合接单数与对应金额。"""
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from models import db
from models.task import Task
from models.website import Website
from routes.stats import stats_bp


def _dt(year, month, day, hour=10, minute=0):
    return datetime(year, month, day, hour, minute, 0)


class StatsOverviewTest(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        app.register_blueprint(stats_bp)
        self.app = app
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _add_website(self, code, name):
        item = Website(code=code, name=name)
        db.session.add(item)
        db.session.flush()
        return item

    def _add_task(
        self,
        create_time,
        is_charged='1',
        price=100,
        website_code='zxzh',
        status='1',
        username=None,
    ):
        task = Task(
            nick_name='测试',
            username=username or f'u{create_time.strftime("%Y%m%d%H%M%S%f")}',
            password='p',
            is_head='1',
            is_charged=is_charged,
            price=price,
            status=status,
            website_code=website_code,
            create_time=create_time,
        )
        db.session.add(task)
        return task

    def _overview(self, start, end):
        return self.client.get(
            '/api/stats/overview',
            query_string={'start': start, 'end': end},
        )

    def test_missing_dates_returns_400(self):
        res = self.client.get('/api/stats/overview')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json()['code'], 400)

    def test_invalid_date_returns_400(self):
        res = self._overview('2026-13-01', '2026-09-01')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json()['code'], 400)

    def test_start_after_end_returns_400(self):
        res = self._overview('2026-09-02', '2026-09-01')
        self.assertEqual(res.status_code, 400)
        body = res.get_json()
        self.assertEqual(body['code'], 400)
        self.assertIn('开始', body['message'])

    def test_amount_sums_price_of_all_orders_by_create_time(self):
        self._add_website('zxzh', '中宣智慧')
        self._add_task(_dt(2026, 8, 10), is_charged='0', price=200)
        self._add_task(_dt(2026, 8, 10), is_charged='1', price=80)
        db.session.commit()

        body = self._overview('2026-08-01', '2026-08-31').get_json()
        self.assertEqual(body['code'], 200)
        rng = body['data']['range']
        self.assertEqual(rng['order_count'], 2)
        self.assertEqual(rng['charged_count'], 1)
        self.assertEqual(rng['free_count'], 1)
        self.assertEqual(rng['revenue'], 280)

    def test_charged_null_price_counts_zero_revenue(self):
        self._add_website('zxzh', '中宣智慧')
        self._add_task(_dt(2026, 8, 11), is_charged='1', price=None)
        db.session.commit()

        rng = self._overview('2026-08-01', '2026-08-31').get_json()['data']['range']
        self.assertEqual(rng['order_count'], 1)
        self.assertEqual(rng['charged_count'], 1)
        self.assertEqual(rng['revenue'], 0)

    def test_daily_groups_by_create_date(self):
        self._add_website('zxzh', '中宣智慧')
        self._add_task(_dt(2026, 8, 10, 9), is_charged='1', price=50, status='2')
        self._add_task(_dt(2026, 8, 10, 18), is_charged='0', price=99, status='1')
        self._add_task(_dt(2026, 8, 12, 1), is_charged='1', price=30, status='1')
        db.session.commit()

        daily = self._overview('2026-08-01', '2026-08-31').get_json()['data']['daily']
        self.assertEqual([row['date'] for row in daily], ['2026-08-12', '2026-08-10'])
        self.assertEqual(daily[0]['order_count'], 1)
        self.assertEqual(daily[0]['revenue'], 30)
        self.assertEqual(daily[0]['pending_count'], 1)
        self.assertEqual(daily[1]['order_count'], 2)
        self.assertEqual(daily[1]['charged_count'], 1)
        self.assertEqual(daily[1]['free_count'], 1)
        self.assertEqual(daily[1]['revenue'], 149)
        self.assertEqual(daily[1]['completed_count'], 1)
        self.assertEqual(daily[1]['pending_count'], 1)

    def test_by_website_range_and_total_revenue(self):
        self._add_website('zxzh', '中宣智慧')
        self._add_website('sczh', '四川智慧')
        self._add_task(_dt(2026, 7, 1), is_charged='1', price=500, website_code='zxzh')
        self._add_task(_dt(2026, 8, 10), is_charged='1', price=100, website_code='zxzh')
        self._add_task(_dt(2026, 8, 11), is_charged='1', price=300, website_code='sczh')
        self._add_task(_dt(2026, 8, 11), is_charged='0', price=90, website_code='sczh')
        db.session.commit()

        data = self._overview('2026-08-01', '2026-08-31').get_json()['data']
        sites = data['by_website']
        self.assertEqual([row['website_code'] for row in sites], ['sczh', 'zxzh'])
        self.assertEqual(sites[0]['website_name'], '四川智慧')
        self.assertEqual(sites[0]['order_count'], 2)
        self.assertEqual(sites[0]['charged_count'], 1)
        self.assertEqual(sites[0]['revenue'], 390)
        self.assertAlmostEqual(sites[0]['revenue_share'], 0.7959)
        self.assertEqual(sites[0]['total_order_count'], 2)
        self.assertEqual(sites[0]['total_revenue'], 390)
        self.assertEqual(sites[1]['revenue'], 100)
        self.assertAlmostEqual(sites[1]['revenue_share'], 0.2041)
        self.assertEqual(sites[1]['total_order_count'], 2)
        self.assertEqual(sites[1]['total_revenue'], 600)
        self.assertEqual(data['range']['revenue'], 490)

    def test_empty_website_code_kept_for_frontend(self):
        self._add_task(_dt(2026, 8, 10), is_charged='1', price=40, website_code='')
        db.session.commit()

        sites = self._overview('2026-08-01', '2026-08-31').get_json()['data']['by_website']
        self.assertEqual(len(sites), 1)
        self.assertEqual(sites[0]['website_code'], '')
        self.assertEqual(sites[0]['website_name'], '')
        self.assertEqual(sites[0]['revenue'], 40)

    def test_today_total_and_range_are_independent(self):
        today = datetime.now().replace(hour=11, minute=0, second=0, microsecond=0)
        older = today - timedelta(days=10)
        outside_range = today - timedelta(days=40)
        self._add_website('zxzh', '中宣智慧')
        self._add_task(today, is_charged='1', price=20)
        self._add_task(older, is_charged='1', price=30)
        self._add_task(outside_range, is_charged='1', price=40)
        db.session.commit()

        start = (today - timedelta(days=29)).strftime('%Y-%m-%d')
        end = today.strftime('%Y-%m-%d')
        data = self._overview(start, end).get_json()['data']
        self.assertEqual(data['today']['order_count'], 1)
        self.assertEqual(data['today']['revenue'], 20)
        self.assertEqual(data['total']['order_count'], 3)
        self.assertEqual(data['total']['revenue'], 90)
        self.assertEqual(data['range']['order_count'], 2)
        self.assertEqual(data['range']['revenue'], 50)

    def test_range_boundaries_are_inclusive(self):
        self._add_website('zxzh', '中宣智慧')
        self._add_task(_dt(2026, 8, 1, 0, 0), is_charged='1', price=10)
        self._add_task(_dt(2026, 8, 31, 23, 59), is_charged='1', price=20)
        self._add_task(_dt(2026, 9, 1, 0, 0), is_charged='1', price=99)
        db.session.commit()

        rng = self._overview('2026-08-01', '2026-08-31').get_json()['data']['range']
        self.assertEqual(rng['order_count'], 2)
        self.assertEqual(rng['revenue'], 30)


if __name__ == '__main__':
    unittest.main()
