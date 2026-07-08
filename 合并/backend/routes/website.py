from flask import Blueprint, request

from models import db
from models.website import Website

website_bp = Blueprint('website', __name__, url_prefix='/api/websites')


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
                Website.remark.like(f'%{keyword}%'),
            )
        )

    pagination = query.order_by(Website.id.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )

    return {
        'code': 200,
        'data': {
            'list': [item.to_dict() for item in pagination.items],
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
    return {'code': 200, 'data': item.to_dict(), 'message': 'success'}


@website_bp.route('', methods=['POST'])
def create_website():
    data = request.get_json() or {}
    item = Website(
        name=data.get('name', ''),
        code=data.get('code'),
        enable_sms_code=data.get('enable_sms_code', '0'),
        remark=data.get('remark'),
    )
    db.session.add(item)
    db.session.commit()
    return {'code': 200, 'data': item.to_dict(), 'message': '创建成功'}


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
    if 'enable_sms_code' in data:
        item.enable_sms_code = data['enable_sms_code']
    if 'remark' in data:
        item.remark = data['remark']

    db.session.commit()
    return {'code': 200, 'data': item.to_dict(), 'message': '更新成功'}


@website_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_website(item_id):
    item = Website.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '网站不存在'}, 404

    db.session.delete(item)
    db.session.commit()
    return {'code': 200, 'message': '删除成功'}
