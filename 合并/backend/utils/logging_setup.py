"""应用日志初始化：控制台 + 按天切割的文件日志。"""
from __future__ import annotations

import logging
import os
from logging.handlers import TimedRotatingFileHandler

_CONFIGURED = False

DEFAULT_FORMAT = '%(asctime)s %(levelname)s [%(name)s] %(message)s'
DEFAULT_DATEFMT = '%Y-%m-%d %H:%M:%S'


def setup_logging(
    *,
    level: int | str | None = None,
    log_dir: str | None = None,
    log_filename: str = 'app.log',
    backup_count: int = 30,
) -> None:
    """配置根 logger：控制台输出 + 按天切割文件（midnight）。

    日志目录默认 backend/logs，可用环境变量 LOG_DIR 覆盖。
    保留天数可用 LOG_BACKUP_COUNT 覆盖（默认 30）。
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    if level is None:
        level_name = (os.getenv('LOG_LEVEL') or 'INFO').upper()
        level = getattr(logging, level_name, logging.INFO)
    elif isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    if log_dir is None:
        log_dir = os.getenv('LOG_DIR') or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'logs',
        )
    backup_count = int(os.getenv('LOG_BACKUP_COUNT', str(backup_count)))

    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_filename)

    formatter = logging.Formatter(DEFAULT_FORMAT, datefmt=DEFAULT_DATEFMT)
    root = logging.getLogger()
    root.setLevel(level)

    # 避免与 basicConfig / 重复调用叠加 handler
    for handler in list(root.handlers):
        root.removeHandler(handler)

    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    root.addHandler(console)

    file_handler = TimedRotatingFileHandler(
        filename=log_path,
        when='midnight',
        interval=1,
        backupCount=backup_count,
        encoding='utf-8',
        utc=False,
    )
    file_handler.suffix = '%Y-%m-%d'
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    _CONFIGURED = True
    logging.getLogger(__name__).info(
        '日志已初始化 level=%s file=%s backup_count=%s',
        logging.getLevelName(level),
        log_path,
        backup_count,
    )
