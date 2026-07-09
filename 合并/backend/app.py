from flask import Flask
from flask_cors import CORS
import logging

from config import Config
from models import db
from routes.website import website_bp
from routes.course import course_bp
from routes.task import task_bp
import services.runners  # noqa: F401  注册任务执行器


def create_app():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r'/api/*': {'origins': '*'}})
    db.init_app(app)

    app.register_blueprint(website_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(task_bp)

    return app


app = create_app()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=6001, debug=True)
