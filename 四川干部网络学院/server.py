from flask import Flask
from urllib.parse import quote_plus as url_quote
from models import db


def create_app():
    app = Flask(__name__)
    # 配置数据库连接
    # 格式: mysql+pymysql://用户名:密码@主机:端口/数据库名
    encoded_password = url_quote("123456")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{encoded_password}@127.0.0.1:3306/test-play-video'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 禁用事件系统以节省开销

    # 配置连接池 (可选但推荐)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True  # 每次使用前检查连接有效性
    }

    # 初始化 db，绑定 app
    db.init_app(app)

    return app
