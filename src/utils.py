import os
import json
from pathlib import Path
from typing import Any, Dict

from loguru import logger
import yaml

ROOT_DIR = Path(__file__).resolve().parents[1]  # 项目根目录
CFG_PATH = ROOT_DIR / "config" / "settings.yaml"
SEEN_PATH = ROOT_DIR / "data" / "seen.json"
OUTPUT_DIR = ROOT_DIR / "data" / "output"
LOG_DIR = ROOT_DIR / "data" / "logs"

LOG_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 配置 loguru
logger.add(LOG_DIR / "run.log", rotation="1 week", encoding="utf-8", enqueue=True, backtrace=True, diagnose=True)


def load_settings() -> Dict[str, Any]:
    if not CFG_PATH.exists():
        raise FileNotFoundError(f"未找到配置文件: {CFG_PATH}")
    with open(CFG_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    # 支持从环境变量覆盖（CI/CD / 临时测试）
    cfg['openai_api_key'] = os.getenv('OPENAI_API_KEY', cfg.get('openai_api_key', ''))
    cfg['wechat_app_id'] = os.getenv('WECHAT_APP_ID', cfg.get('wechat_app_id', ''))
    cfg['wechat_app_secret'] = os.getenv('WECHAT_APP_SECRET', cfg.get('wechat_app_secret', ''))
    cfg['preview_openid'] = os.getenv('WECHAT_PREVIEW_OPENID', cfg.get('preview_openid', ''))
    return cfg


def load_seen() -> set:
    if SEEN_PATH.exists():
        try:
            return set(json.load(open(SEEN_PATH, 'r', encoding='utf-8')))
        except Exception as e:
            logger.warning(f"读取 seen.json 失败，忽略：{e}")
    return set()


def save_seen(seen: set) -> None:
    with open(SEEN_PATH, 'w', encoding='utf-8') as f:
        json.dump(sorted(list(seen)), f, ensure_ascii=False, indent=2)
