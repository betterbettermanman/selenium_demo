from flask import Blueprint, request

from models import db
from models.website import Website
from services.website_browser import is_website_browser_open, open_website_browser

website_bp = Blueprint('website', __name__, url_prefix='/api/websites')


def _enrich_website_dict(item_dict):
    item_dict['browser_open'] = is_website_browser_open(item_dict.get('id'))
    return item_dict


@website_bp.route('', methods=['GET'])
def list_websites():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '', type=str).strip()

    query = Website.query
    if keyword:
        query = query.filter(
            db.or_(
                Website.name.like(f'%{keyword}%'),
                Website.code.like(f'%{keyword}%'),
                Website.url.like(f'%{keyword}%'),
                Website.remark.like(f'%{keyword}%'),
            )
        )

    pagination = query.order_by(Website.id.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )

    return {
        'code': 200,
        'data': {
            'list': [_enrich_website_dict(item.to_dict()) for item in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
        },
        'message': 'success',
    }


@website_bp.route('/<int:item_id>', methods=['GET'])
def get_website(item_id):
    item = Website.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '网站不存在'}, 404
    return {'code': 200, 'data': _enrich_website_dict(item.to_dict()), 'message': 'success'}


@website_bp.route('', methods=['POST'])
def create_website():
    data = request.get_json() or {}
    item = Website(
        name=data.get('name', ''),
        code=data.get('code'),
        url=(data.get('url') or '').strip() or None,
        enable_sms_code=data.get('enable_sms_code', '0'),
        remark=data.get('remark'),
    )
    db.session.add(item)
    db.session.commit()
    return {'code': 200, 'data': _enrich_website_dict(item.to_dict()), 'message': '创建成功'}


@website_bp.route('/<int:item_id>', methods=['PUT'])
def update_website(item_id):
    item = Website.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '网站不存在'}, 404

    data = request.get_json() or {}
    if 'name' in data:
        item.name = data['name']
    if 'code' in data:
        item.code = data['code']
    if 'url' in data:
        item.url = (data.get('url') or '').strip() or None
    if 'enable_sms_code' in data:
        item.enable_sms_code = data['enable_sms_code']
    if 'remark' in data:
        item.remark = data['remark']

    db.session.commit()
    return {'code': 200, 'data': _enrich_website_dict(item.to_dict()), 'message': '更新成功'}


@website_bp.route('/<int:item_id>/open-browser', methods=['POST'])
def open_website_browser_api(item_id):
    item = Website.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '网站不存在'}, 404

    ok, msg = open_website_browser(item)
    if not ok:
        return {'code': 400, 'message': msg}, 400

    return {
        'code': 200,
        'data': _enrich_website_dict(item.to_dict()),
        'message': msg,
    }


@website_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_website(item_id):
    item = Website.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '网站不存在'}, 404

    db.session.delete(item)
    db.session.commit()
    return {'code': 200, 'message': '删除成功'}
