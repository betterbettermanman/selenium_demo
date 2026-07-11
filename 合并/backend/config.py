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
        # 早于 MySQL wait_timeout 回收连接，避免空闲后拿到失效连接
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '280')),
        # 取用连接前先 ping，失效则自动重建
        'pool_pre_ping': True,
        'pool_size': int(os.getenv('DB_POOL_SIZE', '5')),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '10')),
        # pymysql 超时：避免空闲后首次请求在死连接上长时间挂起
        'connect_args': {
            'connect_timeout': int(os.getenv('DB_CONNECT_TIMEOUT', '5')),
            'read_timeout': int(os.getenv('DB_READ_TIMEOUT', '30')),
            'write_timeout': int(os.getenv('DB_WRITE_TIMEOUT', '30')),
        },
    }
