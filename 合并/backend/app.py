from flask import Flask, send_from_directory
from flask_cors import CORS
from sqlalchemy import text
import logging
import os

from config import Config
from models import db
from routes.website import website_bp
from routes.course import course_bp
from routes.task import task_bp
from routes.user_account import user_account_bp
from routes.scheduler import scheduler_bp
from utils.logging_setup import setup_logging
from utils.perf_log import setup_perf_logging
import services.runners  # noqa: F401  注册任务执行器

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')


def create_app():
    setup_logging()
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r'/api/*': {'origins': '*'}})
    db.init_app(app)
    setup_perf_logging(app, app.config['SQLALCHEMY_DATABASE_URI'])

    app.register_blueprint(website_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(user_account_bp)
    app.register_blueprint(scheduler_bp)
    _register_health_route(app)
    _register_frontend_routes(app)

    return app


def _ensure_task_schedule_type_column():
    """兼容已有库：无 schedule_type 列时自动补充。"""
    try:
        exists = db.session.execute(text(
            "SELECT COUNT(*) FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() "
            "AND TABLE_NAME = 'task' AND COLUMN_NAME = 'schedule_type'"
        )).scalar()
        if not exists:
            db.session.execute(text(
                "ALTER TABLE `task` "
                "ADD COLUMN `schedule_type` VARCHAR(16) NOT NULL DEFAULT 'manual' "
                "COMMENT '调度类型（manual：手动，daily：每日，monthly：每月）' "
                "AFTER `status`"
            ))
            db.session.commit()
            logging.info('已自动添加 task.schedule_type 字段')
    except Exception as exc:
        db.session.rollback()
        logging.warning('检查/添加 schedule_type 失败: %s', exc)


def _warmup_db():
    """启动时预热连接池，减少首次请求冷启动耗时。"""
    try:
        db.session.execute(text('SELECT 1'))
        db.session.remove()
        logging.info('数据库连接池预热完成')
    except Exception as exc:
        logging.warning('数据库连接池预热失败: %s', exc)


def _register_health_route(app):
    @app.route('/api/health', methods=['GET'])
    def health_check():
        try:
            db.session.execute(text('SELECT 1'))
            db.session.remove()
            return {'code': 200, 'message': 'ok'}
        except Exception as exc:
            logging.warning('健康检查失败: %s', exc)
            return {'code': 503, 'message': 'database unavailable'}, 503


def _register_frontend_routes(app):
    """打包后由 Flask 托管前端静态资源（backend/static）。"""
    if not os.path.isdir(STATIC_DIR):
        return

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path.startswith('api') or path.startswith('api/'):
            return {'code': 404, 'message': '接口不存在'}, 404
        file_path = os.path.join(STATIC_DIR, path)
        if path and os.path.isfile(file_path):
            return send_from_directory(STATIC_DIR, path)
        return send_from_directory(STATIC_DIR, 'index.html')

    logging.info('已加载前端静态资源: %s', STATIC_DIR)


app = create_app()

with app.app_context():
    try:
        db.create_all()
        _ensure_task_schedule_type_column()
        _warmup_db()
    except Exception as exc:
        logging.warning('应用初始化数据库失败: %s', exc)

try:
    from services.task_scheduler import init_scheduler
    init_scheduler(app)
except Exception as exc:
    logging.warning('调度器初始化失败: %s', exc)


if __name__ == '__main__':
    import sys

    debug = os.getenv('FLASK_DEBUG', '1') == '1'
    port = int(os.getenv('PORT', '6002' if debug else '6001'))
    # PyCharm/pydev 调试时禁用 reloader：子进程重连会因中文路径等触发 UnicodeDecodeError
    under_debugger = (
        os.environ.get('PYCHARM_HOSTED') == '1'
        or 'pydevd' in sys.modules
        or sys.gettrace() is not None
    )
    use_reloader = debug and not under_debugger
    if os.path.isdir(STATIC_DIR):
        logging.info('生产模式: http://0.0.0.0:%s', port)
    else:
        logging.info('开发模式 API: http://0.0.0.0:%s (请单独启动前端 Vite)', port)
    if under_debugger:
        logging.info('检测到调试器，已关闭 Flask reloader')
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=use_reloader)
