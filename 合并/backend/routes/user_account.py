from flask import Blueprint, request

from models import db
from models.user_account import UserAccount
from models.website import Website

user_account_bp = Blueprint('user_account', __name__, url_prefix='/api/user-accounts')


def _enrich_user_account_dict(item_dict):
    website = Website.query.filter_by(code=item_dict.get('website_code')).first()
    item_dict['website_id'] = website.id if website else None
    item_dict['website_name'] = website.name if website else ''
    item_dict['website_url'] = website.url if website else ''
    return item_dict


def _resolve_website(website_id):
    if not website_id:
        return None, {'code': 400, 'message': '请选择网站'}, 400
    website = Website.query.get(website_id)
    if not website:
        return None, {'code': 404, 'message': '网站不存在'}, 404
    return website, None


@user_account_bp.route('', methods=['GET'])
def list_user_accounts():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '', type=str).strip()
    website_id = request.args.get('website_id', type=int)

    query = UserAccount.query
    if website_id:
        website = Website.query.get(website_id)
        if website:
            query = query.filter(UserAccount.website_code == website.code)
    if keyword:
        kw = f'%{keyword}%'
        query = query.outerjoin(Website, UserAccount.website_code == Website.code)
        query = query.filter(
            db.or_(
                UserAccount.nick_name.like(kw),
                UserAccount.organ_name.like(kw),
                UserAccount.username.like(kw),
                UserAccount.website_code.like(kw),
                Website.name.like(kw),
            )
        ).distinct()

    pagination = query.order_by(UserAccount.id.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )

    return {
        'code': 200,
        'data': {
            'list': [_enrich_user_account_dict(item.to_dict()) for item in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
        },
        'message': 'success',
    }


@user_account_bp.route('/<int:item_id>', methods=['GET'])
def get_user_account(item_id):
    item = UserAccount.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '用户不存在'}, 404
    return {'code': 200, 'data': _enrich_user_account_dict(item.to_dict()), 'message': 'success'}


@user_account_bp.route('', methods=['POST'])
def create_user_account():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    nick_name = (data.get('nick_name') or '').strip()
    organ_name = (data.get('organ_name') or '').strip() or None

    if not username:
        return {'code': 400, 'message': '请输入账号'}, 400
    if not password:
        return {'code': 400, 'message': '请输入密码'}, 400

    website, error = _resolve_website(data.get('website_id'))
    if error:
        return error

    item = UserAccount(
        website_code=website.code,
        nick_name=nick_name,
        organ_name=organ_name,
        username=username,
        password=password,
    )
    db.session.add(item)
    db.session.commit()
    return {'code': 200, 'data': _enrich_user_account_dict(item.to_dict()), 'message': '创建成功'}


@user_account_bp.route('/<int:item_id>', methods=['PUT'])
def update_user_account(item_id):
    item = UserAccount.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '用户不存在'}, 404

    data = request.get_json() or {}

    if 'website_id' in data:
        website, error = _resolve_website(data.get('website_id'))
        if error:
            return error
        item.website_code = website.code

    if 'username' in data:
        username = (data.get('username') or '').strip()
        if not username:
            return {'code': 400, 'message': '请输入账号'}, 400
        item.username = username
    if 'password' in data:
        password = (data.get('password') or '').strip()
        if not password:
            return {'code': 400, 'message': '请输入密码'}, 400
        item.password = password
    if 'nick_name' in data:
        item.nick_name = (data.get('nick_name') or '').strip()
    if 'organ_name' in data:
        item.organ_name = (data.get('organ_name') or '').strip() or None

    db.session.commit()
    return {'code': 200, 'data': _enrich_user_account_dict(item.to_dict()), 'message': '更新成功'}


@user_account_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_user_account(item_id):
    item = UserAccount.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '用户不存在'}, 404

    db.session.delete(item)
    db.session.commit()
    return {'code': 200, 'message': '删除成功'}
