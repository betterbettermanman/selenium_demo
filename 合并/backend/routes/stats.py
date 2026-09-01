from datetime import datetime

from flask import Blueprint, request

from services.stats import build_overview

stats_bp = Blueprint('stats', __name__, url_prefix='/api/stats')


def _parse_date(value, label):
    raw = (value or '').strip()
    if not raw:
        return None, f'请提供{label}'
    try:
        return datetime.strptime(raw, '%Y-%m-%d').date(), None
    except ValueError:
        return None, f'{label}格式须为YYYY-MM-DD'


@stats_bp.route('/overview', methods=['GET'])
def get_overview():
    start_date, err = _parse_date(request.args.get('start', ''), '开始日期')
    if err:
        return {'code': 400, 'message': err}, 400
    end_date, err = _parse_date(request.args.get('end', ''), '结束日期')
    if err:
        return {'code': 400, 'message': err}, 400
    if start_date > end_date:
        return {'code': 400, 'message': '开始日期不能晚于结束日期'}, 400

    return {'code': 200, 'data': build_overview(start_date, end_date), 'message': 'success'}
