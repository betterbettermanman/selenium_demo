from flask import Blueprint, request

from models import db
from models.course import Course
from models.website import Website
from utils.json_validate import validate_json_object_or_array

course_bp = Blueprint('course', __name__, url_prefix='/api/courses')


def _enrich_course_dict(course_dict):
    website = Website.query.filter_by(code=course_dict.get('website_code')).first()
    course_dict['website_name'] = website.name if website else ''
    course_dict['website_id'] = website.id if website else None
    return course_dict


def _validate_course_payload(data):
    err = validate_json_object_or_array(data.get('courses'), '特定课表')
    if err:
        return {'code': 400, 'message': err}, 400
    return None


@course_bp.route('', methods=['GET'])
def list_courses():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '', type=str).strip()
    website_id = request.args.get('website_id', type=int)

    query = Course.query
    if website_id:
        website = Website.query.get(website_id)
        if not website:
            return {'code': 404, 'message': '网站不存在'}, 404
        if not website.code:
            return {
                'code': 200,
                'data': {'list': [], 'total': 0, 'page': page, 'page_size': page_size},
                'message': 'success',
            }
        query = query.filter(Course.website_code == website.code)
    if keyword:
        query = query.filter(
            db.or_(
                Course.name.like(f'%{keyword}%'),
                Course.class_id.like(f'%{keyword}%'),
                Course.website_code.like(f'%{keyword}%'),
                Course.remark.like(f'%{keyword}%'),
            )
        )

    pagination = query.order_by(Course.id.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )

    return {
        'code': 200,
        'data': {
            'list': [_enrich_course_dict(item.to_dict()) for item in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
        },
        'message': 'success',
    }


@course_bp.route('/<int:item_id>', methods=['GET'])
def get_course(item_id):
    item = Course.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '课程不存在'}, 404
    return {'code': 200, 'data': _enrich_course_dict(item.to_dict()), 'message': 'success'}


@course_bp.route('', methods=['POST'])
def create_course():
    data = request.get_json() or {}
    error = _validate_course_payload(data)
    if error:
        return error
    item = Course(
        name=data.get('name', ''),
        class_id=data.get('class_id'),
        website_code=data.get('website_code'),
        courses=data.get('courses'),
        remark=data.get('remark'),
    )
    db.session.add(item)
    db.session.commit()
    return {'code': 200, 'data': _enrich_course_dict(item.to_dict()), 'message': '创建成功'}


@course_bp.route('/<int:item_id>', methods=['PUT'])
def update_course(item_id):
    item = Course.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '课程不存在'}, 404

    data = request.get_json() or {}
    if 'courses' in data:
        error = _validate_course_payload(data)
        if error:
            return error
    if 'name' in data:
        item.name = data['name']
    if 'class_id' in data:
        item.class_id = data['class_id']
    if 'website_code' in data:
        item.website_code = data['website_code']
    if 'courses' in data:
        item.courses = data['courses']
    if 'remark' in data:
        item.remark = data['remark']

    db.session.commit()
    return {'code': 200, 'data': _enrich_course_dict(item.to_dict()), 'message': '更新成功'}


@course_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_course(item_id):
    item = Course.query.get(item_id)
    if not item:
        return {'code': 404, 'message': '课程不存在'}, 404

    db.session.delete(item)
    db.session.commit()
    return {'code': 200, 'message': '删除成功'}
