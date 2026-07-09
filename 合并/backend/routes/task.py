from flask import Blueprint, request, current_app

from models import db
from models.course import Course
from models.task import Task
from models.website import Website
from services.task_runner import (
    get_runner,
    is_task_running,
    resend_sms_code,
    start_task,
    stop_task,
    submit_sms_code,
)
from services.task_runner import RunnerPhase

task_bp = Blueprint('task', __name__, url_prefix='/api/tasks')


def _enrich_task_dict(task_dict):
    website = Website.query.filter_by(code=task_dict.get('website_code')).first()
    course = None
    if task_dict.get('class_id') and task_dict.get('website_code'):
        course = Course.query.filter_by(
            class_id=task_dict['class_id'],
            website_code=task_dict['website_code'],
        ).first()
    task_dict['website_id'] = website.id if website else None
    task_dict['website_name'] = website.name if website else ''
    task_dict['course_id'] = course.id if course else None
    task_dict['course_name'] = course.name if course else ''
    task_dict['is_running'] = is_task_running(task_dict.get('id'))
    runner = get_runner(task_dict.get('id'))
    task_dict['waiting_sms'] = (
        runner is not None and runner.phase == RunnerPhase.WAITING_SMS
    )
    task_dict['enable_sms_code'] = website.enable_sms_code if website else '0'
    return task_dict


def _parse_is_charged(value) -> str:
    return '1' if str(value) in ('1', 'true', 'True', True) else '0'


def _parse_price(value):
    if value is None or value == '':
        return None
    try:
        num = float(value)
    except (TypeError, ValueError):
        return False
    if num < 0 or num != int(num):
        return False
    return int(num)


def _resolve_website_and_course(website_id, course_id):
    if not website_id:
        return None, {'code': 400, 'message': '请选择网站'}, 400
    if not course_id:
        return None, {'code': 400, 'message': '请选择课程'}, 400

    website = Website.query.get(website_id)
    if not website:
        return None, {'code': 404, 'message': '网站不存在'}, 404

    course = Course.query.get(course_id)
    if not course:
        return None, {'code': 404, 'message': '课程不存在'}, 404

    if course.website_code != website.code:
        return None, {'code': 400, 'message': '课程不属于所选网站'}, 400

    return (website, course), None


@task_bp.route('', methods=['GET'])
def list_tasks():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '', type=str).strip()
    status = request.args.get('status', '', type=str).strip()

    query = Task.query
    if keyword:
        query = query.filter(
            db.or_(
                Task.nick_name.like(f'%{keyword}%'),
                Task.username.like(f'%{keyword}%'),
                Task.organ_name.like(f'%{keyword}%'),
                Task.website_code.like(f'%{keyword}%'),
                Task.remark.like(f'%{keyword}%'),
            )
        )
    if status:
        query = query.filter(Task.status == status)

    pagination = query.order_by(Task.id.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )

    return {
        'code': 200,
        'data': {
            'list': [_enrich_task_dict(item.to_dict()) for item in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
        },
        'message': 'success',
    }


@task_bp.route('/<int:item_id>', methods=['GET'])
def get_task(item_id):
    item = Task.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '任务不存在'}, 404
    return {'code': 200, 'data': _enrich_task_dict(item.to_dict()), 'message': 'success'}


@task_bp.route('', methods=['POST'])
def create_task():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    remark = data.get('remark')
    nick_name = (data.get('nick_name') or '').strip()
    is_charged = _parse_is_charged(data.get('is_charged', '0'))
    price = _parse_price(data.get('price'))
    if price is False:
        return {'code': 400, 'message': '价格须为非负整数'}, 400

    if not username:
        return {'code': 400, 'message': '请输入账号'}, 400
    if not password:
        return {'code': 400, 'message': '请输入密码'}, 400

    result, error = _resolve_website_and_course(data.get('website_id'), data.get('course_id'))
    if error:
        return error
    website, course = result

    item = Task(
        nick_name=nick_name,
        username=username,
        password=password,
        remark=remark,
        website_code=website.code,
        class_id=course.class_id,
        courses=course.courses,
        is_head=data.get('is_head', '1'),
        is_charged=is_charged,
        price=price,
        status='1',
    )
    db.session.add(item)
    db.session.commit()
    return {'code': 200, 'data': _enrich_task_dict(item.to_dict()), 'message': '创建成功'}


@task_bp.route('/<int:item_id>', methods=['PUT'])
def update_task(item_id):
    item = Task.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '任务不存在'}, 404

    data = request.get_json() or {}

    if 'website_id' in data or 'course_id' in data:
        website_id = data.get('website_id')
        course_id = data.get('course_id')
        if not website_id and item.website_code:
            website = Website.query.filter_by(code=item.website_code).first()
            website_id = website.id if website else None
        if not course_id and item.class_id and item.website_code:
            course = Course.query.filter_by(
                class_id=item.class_id,
                website_code=item.website_code,
            ).first()
            course_id = course.id if course else None
        result, error = _resolve_website_and_course(website_id, course_id)
        if error:
            return error
        website, course = result
        item.website_code = website.code
        item.class_id = course.class_id
        item.courses = course.courses

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
    if 'remark' in data:
        item.remark = data['remark']

    if 'is_charged' in data:
        item.is_charged = _parse_is_charged(data.get('is_charged'))
    if 'price' in data:
        price = _parse_price(data.get('price'))
        if price is False:
            return {'code': 400, 'message': '价格须为非负整数'}, 400
        item.price = price

    simple_fields = ['nick_name', 'organ_name', 'is_head', 'status', 'no_play_videos']
    for field in simple_fields:
        if field in data:
            setattr(item, field, data[field])

    db.session.commit()
    return {'code': 200, 'data': _enrich_task_dict(item.to_dict()), 'message': '更新成功'}


@task_bp.route('/<int:item_id>/start', methods=['POST'])
def start_task_api(item_id):
    item = Task.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '任务不存在'}, 404

    app = current_app._get_current_object()
    ok, result = start_task(item_id, app)
    if not ok:
        return {'code': 400, 'message': result.get('message', '启动失败')}, 400

    return {
        'code': 200,
        'data': {
            **_enrich_task_dict(item.to_dict()),
            'need_sms': result.get('need_sms', False),
        },
        'message': result.get('message', '任务已启动'),
    }


@task_bp.route('/<int:item_id>/sms-code', methods=['POST'])
def submit_sms_code_api(item_id):
    item = Task.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '任务不存在'}, 404

    data = request.get_json() or {}
    code = (data.get('code') or '').strip()
    if not code:
        return {'code': 400, 'message': '请输入手机验证码'}, 400

    app = current_app._get_current_object()
    ok, msg = submit_sms_code(item_id, code, app)
    if not ok:
        return {'code': 400, 'message': msg}, 400

    return {
        'code': 200,
        'data': _enrich_task_dict(item.to_dict()),
        'message': msg,
    }


@task_bp.route('/<int:item_id>/stop', methods=['POST'])
def stop_task_api(item_id):
    item = Task.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '任务不存在'}, 404

    app = current_app._get_current_object()
    ok, msg = stop_task(item_id, app)
    if not ok:
        return {'code': 400, 'message': msg}, 400

    return {
        'code': 200,
        'data': _enrich_task_dict(item.to_dict()),
        'message': msg,
    }


@task_bp.route('/<int:item_id>/resend-sms', methods=['POST'])
def resend_sms_code_api(item_id):
    item = Task.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '任务不存在'}, 404

    app = current_app._get_current_object()
    ok, msg = resend_sms_code(item_id, app)
    if not ok:
        return {'code': 400, 'message': msg}, 400

    return {'code': 200, 'message': msg}


@task_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_task(item_id):
    item = Task.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '任务不存在'}, 404

    db.session.delete(item)
    db.session.commit()
    return {'code': 200, 'message': '删除成功'}
