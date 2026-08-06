"""调度配置读写（JSON 文件，可供 UI 修改）。"""
from __future__ import annotations

import json
import logging
import os
import re
import threading
from copy import deepcopy

logger = logging.getLogger(__name__)

_LOCK = threading.Lock()
_CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
_CONFIG_PATH = os.path.join(_CONFIG_DIR, 'scheduler_config.json')

DEFAULT_CONFIG = {
    'max_running_tasks': 5,
    'daily_time': '08:00',
    'monthly_day': 1,
    'monthly_time': '08:00',
}

_TIME_RE = re.compile(r'^([01]?\d|2[0-3]):([0-5]\d)$')


def _ensure_dir():
    os.makedirs(_CONFIG_DIR, exist_ok=True)


def get_scheduler_config() -> dict:
    with _LOCK:
        if not os.path.isfile(_CONFIG_PATH):
            return deepcopy(DEFAULT_CONFIG)
        try:
            with open(_CONFIG_PATH, 'r', encoding='utf-8') as f:
                raw = json.load(f) or {}
        except Exception:
            logger.exception('读取调度配置失败，使用默认值')
            return deepcopy(DEFAULT_CONFIG)
        cfg = deepcopy(DEFAULT_CONFIG)
        cfg.update({k: raw[k] for k in DEFAULT_CONFIG if k in raw})
        return cfg


def validate_scheduler_config(data: dict) -> tuple[dict | None, str]:
    cfg = deepcopy(DEFAULT_CONFIG)
    if not isinstance(data, dict):
        return None, '配置须为对象'

    if 'max_running_tasks' in data:
        try:
            max_n = int(data['max_running_tasks'])
        except (TypeError, ValueError):
            return None, '最大并发须为正整数'
        if max_n < 1:
            return None, '最大并发须 >= 1'
        cfg['max_running_tasks'] = max_n

    for key in ('daily_time', 'monthly_time'):
        if key in data:
            value = str(data.get(key) or '').strip()
            match = _TIME_RE.match(value)
            if not match:
                return None, f'{key} 格式须为 HH:MM'
            hour, minute = int(match.group(1)), int(match.group(2))
            cfg[key] = f'{hour:02d}:{minute:02d}'

    if 'monthly_day' in data:
        try:
            day = int(data['monthly_day'])
        except (TypeError, ValueError):
            return None, '每月触发日须为 1-28 的整数'
        if day < 1 or day > 28:
            return None, '每月触发日须在 1-28（避免月末差异）'
        cfg['monthly_day'] = day

    # 合并未传入字段为当前已保存值
    current = get_scheduler_config()
    for key in DEFAULT_CONFIG:
        if key not in data:
            cfg[key] = current[key]
    return cfg, ''


def save_scheduler_config(data: dict) -> tuple[dict | None, str]:
    cfg, err = validate_scheduler_config(data)
    if err:
        return None, err
    with _LOCK:
        _ensure_dir()
        with open(_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    logger.info('调度配置已保存: %s', cfg)
    return cfg, ''


def parse_hhmm(value: str) -> tuple[int, int]:
    match = _TIME_RE.match((value or '').strip())
    if not match:
        return 8, 0
    return int(match.group(1)), int(match.group(2))
