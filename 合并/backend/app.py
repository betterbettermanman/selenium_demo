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
from utils.perf_log import setup_perf_logging
import services.runners  # noqa: F401  注册任务执行器

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')


def create_app():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r'/api/*': {'origins': '*'}})
    db.init_app(app)
    setup_perf_logging(app, app.config['SQLALCHEMY_DATABASE_URI'])

    app.register_blueprint(website_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(user_account_bp)
    _register_health_route(app)
    _register_frontend_routes(app)

    return app


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
        _warmup_db()
    except Exception as exc:
        logging.warning('应用初始化数据库失败: %s', exc)


if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', '1') == '1'
    port = int(os.getenv('PORT', '6002' if debug else '6001'))
    if os.path.isdir(STATIC_DIR):
        logging.info('生产模式: http://0.0.0.0:%s', port)
    else:
        logging.info('开发模式 API: http://0.0.0.0:%s (请单独启动前端 Vite)', port)
    app.run(host='0.0.0.0', port=port, debug=debug)
