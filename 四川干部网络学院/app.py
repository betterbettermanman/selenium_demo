# app.py
import re
import threading
from typing import Dict

from flask import request, jsonify, current_app
from flask_cors import CORS  # 导入 CORS
from loguru import logger

from models import db, ScgbTask, ScgbCourse  # 导入 db 实例和模型
from scgb import TeacherTrainingChecker, open_init_browser, remove_browser_dir
from server import create_app

app = create_app()

# ✅ 允许所有域名访问所有路由
CORS(app)

running_tasks: Dict[str, TeacherTrainingChecker] = {}


@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'code': 200, 'msg': 'ping'})


@app.route('/api/task_list', methods=['GET'])
def task_list():
    """获取所有用户"""
    tasks = ScgbTask.query.all()
    return jsonify({'code': 200, 'msg': '', 'data': [task.to_dict() for task in tasks]})


@app.route('/api/task_page', methods=['GET'])
def get_task_page():
    """获取任务列表（分页，支持 pageNo/pageSize）"""
    # ✅ 接收前端传来的 pageNo 和 pageSize
    page_no = request.args.get('pageNo', 1, type=int)  # 当前页码，从1开始
    page_size = request.args.get('pageSize', 10, type=int)  # 每页数量

    # ✅ 接收查询条件
    username = request.args.get('name', '', type=str).strip()  # 支持模糊查询
    is_running = request.args.get('is_running', '', type=str).strip()  # 支持模糊查询
    status = request.args.get('status', '', type=str).strip()  # 支持模糊查询

    # 限制每页最大数量
    if page_size > 100:
        page_size = 100

    # ✅ 构建查询：按 create_time 倒序排列
    query = ScgbTask.query.order_by(ScgbTask.id.desc())
    # ✅ 如果提供了 username，添加模糊查询条件（包含即可）
    if username:
        if re.search(r'\d', username):  # \d 表示任意数字
            logger.info("✅ username 包含数字")
            query = query.filter(ScgbTask.username.ilike(f'%{username}%'))
        else:
            logger.info("❌ username 不包含数字")
            query = query.filter(ScgbTask.nick_name.ilike(f'%{username}%'))
    if is_running:
        query = query.filter(ScgbTask.is_running == is_running)
    if status:
        query = query.filter(ScgbTask.status == status)
    # ✅ 执行分页
    pagination = query.paginate(
        page=page_no,
        per_page=page_size,
        error_out=False
    )

    tasks = pagination.items

    for task in tasks:
        if task.username in running_tasks:
            if running_tasks[task.username].is_running == "1":
                task.is_running = "1"
            elif running_tasks[task.username].is_running == "2":
                task.is_running = "2"
            else:
                task.is_running = "0"
        else:
            task.is_running = "0"
        if task.status == "2":
            task.status = "1"
        else:
            task.status = "0"
    return jsonify({
        'code': 200,
        'msg': '',
        'data': {
            'list': [task.to_dict() for task in tasks],
            'total': pagination.total,  # 总记录数
            'pageNo': pagination.page,  # 当前页码
            'pageSize': pagination.per_page,  # 每页数量
            'pages': pagination.pages,  # 总页数
            'hasNext': pagination.has_next,  # 是否有下一页
            'hasPrev': pagination.has_prev,  # 是否有上一页
        }
    })


@app.route('/api/delete_task', methods=['GET'])
def delete_task():
    id = request.args.get('id', 1, type=int)  # 当前页码，从1开始
    """删除指定 ID 的用户"""
    # 1. 根据 ID 查询用户
    task = ScgbTask.query.get(id)

    if not task:
        return jsonify({
            'code': 500,
            'msg': '任务不存在'
        })

    # 2. 执行删除
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({
            'code': 200,
            'msg': '任务删除成功',
            'data': {}
        })
    except Exception as e:
        db.session.rollback()  # 出错回滚
        return jsonify({
            'code': 500,
            'msg': '删除失败，数据库错误',
            'error': str(e)
        })


# -------------------------------------------------------
# 接口1：新建任务
# POST /api/tasks
# -------------------------------------------------------
@app.route('/api/create_task', methods=['POST'])
def create_task():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'msg': '请求数据不能为空'}), 400

        # 校验必要字段
        required_fields = ['username', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'code': 400, 'msg': f'缺少必要字段: {field}'}), 400

        # 第一种情况，不存在username，使用username和password进行登录验证，验证通过，即说明用户名和密码正确。
        history_task = ScgbTask.query.filter(ScgbTask.username == data['username']).first()
        if history_task:
            return jsonify({'code': 500, 'msg': f'当前账号已存在'}), 200
        # 创建新任务
        new_task = ScgbTask(
            username=data['username'],
            password=data['password'],  # 生产环境建议加密存储
            is_head='0',  # 确保是字符串
            no_play_videos=[],  # 可选字段
            status=data.get('status', '1')  # 默认为“未完成”
        )

        logger.info("创建对象，执行任务")
        check = TeacherTrainingChecker("", new_task.username, new_task.password,
                                       new_task.is_head)
        success, msg = check.check_login()
        if success == "1":
            db.session.add(new_task)
            db.session.commit()
            check.id = new_task.id
            running_tasks[new_task.username] = check
            return jsonify({
                'code': 200,
                'msg': '任务创建成功，接受手机验证码',
                'data': new_task.id
            }), 200
        elif success == "0":
            # 优化点，池化driver
            check.driver.close()
            # 账号密码错误
            return jsonify({
                'code': 500,
                'msg': f'任务创建失败【{msg}】',
                'data': ""
            }), 200
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'服务器错误: {str(e)}'}), 200


# -------------------------------------------------------
# 接口1：强制重新执行任务
# POST /api/force_restart_task
# -------------------------------------------------------
@app.route('/api/force_restart_task', methods=['POST'])
def force_restart_task():
    data = request.get_json()
    if not data:
        return jsonify({'code': 500, 'msg': '请求数据不能为空'})

    # 校验必要字段
    required_fields = ['id']
    for field in required_fields:
        if field not in data:
            return jsonify({'code': 500, 'msg': f'缺少必要字段: {field}'})
    id = data['id']
    current_task = ScgbTask.query.get_or_404(id)
    # 删除浏览器实例
    remove_browser_dir(current_task.username)
    # if running_tasks.keys().__contains__(current_task.username):
    #     return jsonify({'code': 500, 'msg': '当前任务正在执行中'})
    check = TeacherTrainingChecker(current_task.id, current_task.username, current_task.password,
                                   isHead=current_task.is_head,
                                   class_id=current_task.class_id, courses=current_task.courses)
    success, msg = check.check_login()
    if success == "2":
        running_tasks[current_task.username] = check

        """启动异步线程，在新线程中初始化上下文"""

        def thread_target():
            # 1. 新线程中创建应用实例（或获取已存在的）
            app = create_app() if not current_app else current_app._get_current_object()

            # 2. 手动推送应用上下文（关键步骤）
            with app.app_context():
                # 3. 执行核心任务（此时已在上下文内，可正常操作数据库）
                check.exec_main()

        # 启动线程
        thread = threading.Thread(target=thread_target)
        thread.start()
        return jsonify({
            'code': 200,
            'msg': '任务继续执行',
            'data': {"status": "1"}
        }), 200
    elif success == "1":
        running_tasks[current_task.username] = check
        return jsonify({
            'code': 200,
            'msg': '任务创建成功，接受手机验证码',
            'data': {"status": "0"}
        }), 200
    else:
        return jsonify({
            'code': 500,
            'msg': f'任务创建失败，{msg}',
        })


# -------------------------------------------------------
# 接口1：重新执行任务
# POST /api/restart_task
# -------------------------------------------------------
@app.route('/api/restart_task', methods=['POST'])
def restart_task():
    data = request.get_json()
    if not data:
        return jsonify({'code': 500, 'msg': '请求数据不能为空'})

    # 校验必要字段
    required_fields = ['id']
    for field in required_fields:
        if field not in data:
            return jsonify({'code': 500, 'msg': f'缺少必要字段: {field}'})
    id = data['id']
    current_task = ScgbTask.query.get_or_404(id)
    # 判断当前任务是否完成，完成状态不可继续执行
    if current_task.status == "2":
        return jsonify({'code': 500, 'msg': '任务已完成'})
    # 判断当前用户是否正在接受验证码
    if running_tasks.__contains__(current_task.username):
        logger.info("当前浏览器已启动")
        if running_tasks[current_task.username].is_running == "1":
            return jsonify({'code': 500, 'msg': '当前任务正在运行中'})
        elif running_tasks[current_task.username].is_running == "2":
            return jsonify({'code': 200, 'msg': '任务创建成功，接受手机验证码', 'data': {"status": "0"}})

    check = TeacherTrainingChecker(current_task.id, current_task.username, current_task.password,
                                   isHead=current_task.is_head,
                                   class_id=current_task.class_id, courses=current_task.courses)
    success, msg = check.check_login()
    if success == "2":
        running_tasks[current_task.username] = check

        """启动异步线程，在新线程中初始化上下文"""

        def thread_target():
            # 1. 新线程中创建应用实例（或获取已存在的）
            app = create_app() if not current_app else current_app._get_current_object()

            # 2. 手动推送应用上下文（关键步骤）
            with app.app_context():
                # 3. 执行核心任务（此时已在上下文内，可正常操作数据库）
                check.exec_main()

        # 启动线程
        thread = threading.Thread(target=thread_target)
        thread.start()
        return jsonify({
            'code': 200,
            'msg': '任务继续执行',
            'data': {"status": "1"}
        }), 200
    elif success == "1":
        running_tasks[current_task.username] = check
        return jsonify({
            'code': 200,
            'msg': '任务创建成功，接受手机验证码',
            'data': {"status": "0"}
        }), 200
    else:
        return jsonify({
            'code': 500,
            'msg': f'任务创建失败，{msg}',
        })


# -------------------------------------------------------
# 接口1：重新发送手机验证码
# POST /api/submit
# -------------------------------------------------------
@app.route('/api/resend_phone_code', methods=['POST'])
def resend_phone_code():
    data = request.get_json()
    if not data:
        return jsonify({'code': 500, 'msg': '请求数据不能为空'})

    # 校验必要字段
    required_fields = ['id']
    for field in required_fields:
        if field not in data:
            return jsonify({'code': 500, 'msg': f'缺少必要字段: {field}'})
    current_task = ScgbTask.query.get_or_404(data['id'])
    check = running_tasks[current_task.username]
    success, msg = check.resend_code()
    if success:
        return jsonify({'code': 200, 'msg': '发送成功'})
    else:
        return jsonify({'code': 500, 'msg': msg})


# -------------------------------------------------------
# 接口1：提交手机验证码
# POST /api/submit
# -------------------------------------------------------
@app.route('/api/submit_phone_code', methods=['POST'])
def submit_phone_code():
    data = request.get_json()
    if not data:
        return jsonify({'code': 500, 'msg': '请求数据不能为空'})

    # 校验必要字段
    required_fields = ['id', 'code']
    for field in required_fields:
        if field not in data:
            return jsonify({'code': 500, 'msg': f'缺少必要字段: {field}'})
    current_task = ScgbTask.query.get_or_404(data['id'])
    check = running_tasks[current_task.username]
    success, msg = check.validate_code(data['code'])
    if success:
        if current_task.class_id or current_task.courses:
            """启动异步线程，在新线程中初始化上下文"""

            def thread_target():
                # 1. 新线程中创建应用实例（或获取已存在的）
                app = create_app() if not current_app else current_app._get_current_object()

                # 2. 手动推送应用上下文（关键步骤）
                with app.app_context():
                    # 3. 执行核心任务（此时已在上下文内，可正常操作数据库）
                    check.exec_main()

            # 启动线程
            thread = threading.Thread(target=thread_target)
            thread.start()
            return jsonify({'code': 200, 'msg': '验证成功，开始学习'}), 200
        else:
            return jsonify({'code': 200, 'msg': '验证成功，请选择课程'}), 200
    else:
        return jsonify({'code': 500, 'msg': f'验证码错误'}), 200


# 课程列表
@app.route('/api/course_list', methods=['GET'])
def course_list():
    id = request.args.get('id', '', type=str).strip()  # 支持模糊查询
    current_task = ScgbTask.query.get_or_404(id)
    check = running_tasks[current_task.username]
    tasks = check.course_list()
    logger.info(tasks)
    # 如果课程列表为空，查询自定义课程列表
    data = tasks['result']['records']
    if not data:
        new_data = [course.to_dict() for course in ScgbCourse.query.all()]
    else:
        new_data = [{'id': item['id'], 'class_id': item['id'], 'name': item['name']} for item in data]

    return jsonify({'code': 200, 'data': new_data, 'msg': ''})


# 选择课程，提交任务
@app.route('/api/submit_course', methods=['POST'])
def submit_course():
    data = request.get_json()
    if not data:
        return jsonify({'code': 500, 'msg': '请求数据不能为空'})
    # 校验必要字段
    required_fields = ['id', 'class_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'code': 500, 'msg': f'缺少必要字段: {field}'})
    class_id = data['class_id']
    id = data['id']
    current_task = ScgbTask.query.get_or_404(id)
    check = running_tasks[current_task.username]
    # 判断当前课程是自定义课程，还是官方课程
    course_info = ScgbCourse.query.filter(ScgbCourse.id == class_id).first()
    if course_info:
        # 自定义
        check.class_id = course_info.class_id
        check.courses = course_info.courses
        ScgbTask.update_by_id(current_task.id, class_id=course_info.class_id, courses=course_info.courses)
    else:
        check.class_id = class_id
        ScgbTask.update_by_id(current_task.id, class_id=class_id)

    """启动异步线程，在新线程中初始化上下文"""

    def thread_target():
        # 1. 新线程中创建应用实例（或获取已存在的）
        app = create_app() if not current_app else current_app._get_current_object()

        # 2. 手动推送应用上下文（关键步骤）
        with app.app_context():
            # 3. 执行核心任务（此时已在上下文内，可正常操作数据库）
            check.exec_main()

    # 启动线程
    thread = threading.Thread(target=thread_target)
    thread.start()

    # 如果课程列表为空，查询自定义课程列表
    return jsonify({'code': 200, 'msg': '选择成功，开始学习'})


# 打开浏览器
@app.route('/api/open_browser', methods=['POST'])
def open_browser():
    data = request.get_json()
    if not data:
        return jsonify({'code': 500, 'msg': '请求数据不能为空'})
    # 校验必要字段
    required_fields = ['id']
    for field in required_fields:
        if field not in data:
            return jsonify({'code': 500, 'msg': f'缺少必要字段: {field}'})
    id = data['id']
    current_task = ScgbTask.query.get_or_404(id)
    thread = threading.Thread(target=open_init_browser, args=[current_task.username])
    thread.start()
    # open_init_browser(current_task.username)

    # 如果课程列表为空，查询自定义课程列表
    return jsonify({'code': 200, 'msg': '打开成功，请稍等'})


# 关闭浏览器
@app.route('/api/close_browser', methods=['POST'])
def close_browser():
    data = request.get_json()
    if not data:
        return jsonify({'code': 500, 'msg': '请求数据不能为空'})
    # 校验必要字段
    required_fields = ['id']
    for field in required_fields:
        if field not in data:
            return jsonify({'code': 500, 'msg': f'缺少必要字段: {field}'})
    id = data['id']
    current_task = ScgbTask.query.get_or_404(id)
    if current_task.username in running_tasks:
        check = running_tasks[current_task.username]
        check.close_browser()
        return jsonify({'code': 200, 'msg': '关闭成功'})
    else:
        return jsonify({'code': 500, 'msg': '浏览器不存在'})


from flask_apscheduler import APScheduler

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# # ✅ 使用 @scheduler.task 装饰器
# @scheduler.task('interval', id='clean_logs', seconds=60)
# def clean_logs():
#     with app.app_context():
#         logger.info("判断任务是否在执行，没有执行的，进行重跑，如果登陆过期的，就行登陆通知")
#         for task in running_tasks.values():
#             if not task.is_running and task.is_login and not task.is_complete:
#                 logger.info("任务停止，并且当前登陆未过期，判断当前任务是否过期")
#                 check = TeacherTrainingChecker(task.id, task.username, task.password,
#                                                task.is_headless, class_id=task.class_id, courses=task.courses)
#                 running_tasks[task.username] = check
#
#                 """启动异步线程，在新线程中初始化上下文"""
#
#                 def thread_target():
#                     # 1. 新线程中创建应用实例（或获取已存在的）
#                     app = create_app() if not current_app else current_app._get_current_object()
#
#                     # 2. 手动推送应用上下文（关键步骤）
#                     with app.app_context():
#                         # 3. 执行核心任务（此时已在上下文内，可正常操作数据库）
#                         check.exec_main()
#
#                 # 启动线程
#                 thread = threading.Thread(target=thread_target)
#                 thread.start()


# 运行应用
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5002)
