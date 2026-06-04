"""应用配置：全部来自环境变量，便于独立部署。

支持从项目根目录的 .env 文件加载（如果存在），方便本地开发。
"""

from __future__ import annotations

import os
from functools import lru_cache


def _load_dotenv() -> None:
    """极简 .env 加载器，避免引入额外强依赖。

    仅在对应环境变量尚未设置时才写入，命令行/系统环境变量优先级更高。
    """
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if not os.path.isfile(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except OSError:
        # 加载失败不应阻断启动，仅依赖系统环境变量即可
        pass


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


class Settings:
    """运行时配置。"""

    def __init__(self) -> None:
        _load_dotenv()

        # ---- MySQL 连接配置 ----
        self.db_host: str = os.getenv("DB_HOST", "127.0.0.1")
        self.db_port: int = _get_int("DB_PORT", 3306)
        self.db_user: str = os.getenv("DB_USER", "root")
        self.db_password: str = os.getenv("DB_PASSWORD", "")
        self.db_name: str = os.getenv("DB_NAME", "")
        self.db_charset: str = os.getenv("DB_CHARSET", "utf8mb4")

        # 连接池配置
        self.db_pool_min: int = _get_int("DB_POOL_MIN", 1)
        self.db_pool_max: int = _get_int("DB_POOL_MAX", 10)
        self.db_connect_timeout: int = _get_int("DB_CONNECT_TIMEOUT", 10)

        # ---- 认证配置：固定 KEY ----
        # 客户端通过请求头 X-API-Key 传入；与该值一致即放行。
        self.api_key: str = os.getenv("API_KEY", "change-me-please")
        self.api_key_header: str = os.getenv("API_KEY_HEADER", "X-API-Key")

        # ---- 业务/分页配置 ----
        self.default_page_size: int = _get_int("DEFAULT_PAGE_SIZE", 10)
        self.max_page_size: int = _get_int("MAX_PAGE_SIZE", 100)

        # 申报时间过滤起点（与给定 SQL 保持一致，可按需调整）
        self.create_time_after: str = os.getenv(
            "CREATE_TIME_AFTER", "2024-05-31 00:00:00"
        )
        # 申报成功状态值
        self.apply_status: str = os.getenv("APPLY_STATUS", "check_doing")

        # 建设简介内容字段：给定 SQL 中未包含该列，schema 也未知。
        # 若数据库中存在该列（如 content / remark / build_content），
        # 在此配置列名即可自动纳入查询；留空则该字段返回 null。
        self.brief_column: str = os.getenv("BRIEF_COLUMN", "").strip()

        # ---- 服务配置 ----
        self.app_host: str = os.getenv("APP_HOST", "0.0.0.0")
        self.app_port: int = _get_int("APP_PORT", 8000)
        self.debug: bool = _get_bool("DEBUG", False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
