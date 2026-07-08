import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_URI = 'mysql+pymysql://root:123456@localhost:3306/task_manager?charset=utf8mb4'


def _build_database_uri() -> str:
    """从独立环境变量构建连接串，密码/用户名中的特殊字符会自动 URL 编码。"""
    has_db_config = any(
        os.getenv(k) for k in ('DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME')
    )
    if has_db_config:
        user = quote_plus(os.getenv('DB_USER', 'root'))
        password = quote_plus(os.getenv('DB_PASSWORD', ''))
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '3306')
        name = os.getenv('DB_NAME', 'task_manager')
        return f'mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4'
    return os.getenv('DATABASE_URL', _DEFAULT_URI)


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
