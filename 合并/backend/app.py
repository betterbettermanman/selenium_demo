from flask import Flask, send_from_directory
from flask_cors import CORS
import logging
import os

from config import Config
from models import db
from routes.website import website_bp
from routes.course import course_bp
from routes.task import task_bp
import services.runners  # noqa: F401  注册任务执行器

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')


def create_app():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r'/api/*': {'origins': '*'}})
    db.init_app(app)

    app.register_blueprint(website_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(task_bp)
    _register_frontend_routes(app)

    return app


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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    debug = os.getenv('FLASK_DEBUG', '1') == '1'
    port = int(os.getenv('PORT', '6002' if debug else '6001'))
    if os.path.isdir(STATIC_DIR):
        logging.info('生产模式: http://0.0.0.0:%s', port)
    else:
        logging.info('开发模式 API: http://0.0.0.0:%s (请单独启动前端 Vite)', port)
    app.run(host='0.0.0.0', port=port, debug=debug)
