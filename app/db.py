"""数据库访问层：连接池管理与给定 SQL 的分页查询。

设计要点：
- 使用 PyMySQL + DBUtils.PooledDB 维护连接池，避免每次请求新建连接。
- 给定 SQL 中的状态值、时间过滤通过占位符参数化，杜绝 SQL 注入。
- 分页通过 COUNT 总数 + LIMIT/OFFSET 实现。
"""

from __future__ import annotations

import re
import threading
from typing import Any, Optional

import pymysql
from dbutils.pooled_db import PooledDB

from .config import Settings, get_settings

_pool: Optional[PooledDB] = None
_pool_lock = threading.Lock()

# 合法列名（库表自动生成场景下仅允许字母、数字、下划线）
_COLUMN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _build_pool(settings: Settings) -> PooledDB:
    return PooledDB(
        creator=pymysql,
        mincached=settings.db_pool_min,
        maxconnections=settings.db_pool_max,
        blocking=True,
        ping=1,  # 取连接时检测可用性
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
        charset=settings.db_charset,
        connect_timeout=settings.db_connect_timeout,
        cursorclass=pymysql.cursors.DictCursor,
    )


def get_pool() -> PooledDB:
    """获取（惰性初始化）全局连接池。"""
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = _build_pool(get_settings())
    return _pool


def _safe_brief_column(brief_column: str) -> Optional[str]:
    """校验建设简介列名，防止 SQL 注入；非法或为空返回 None。"""
    if not brief_column:
        return None
    if not _COLUMN_RE.match(brief_column):
        raise ValueError(f"非法的 BRIEF_COLUMN 配置: {brief_column!r}")
    return brief_column


def _build_select_clause(brief_column: Optional[str]) -> str:
    columns = [
        "project_temp_apply.name AS project_name",
        "system_dept.name AS declare_dept",
        "system_users.nickname AS contact_person",
        "project_temp_apply.manager_phone AS contact_phone",
        "project_temp_apply.create_time AS declare_time",
    ]
    if brief_column:
        columns.insert(2, f"project_temp_apply.{brief_column} AS construction_brief")
    else:
        columns.insert(2, "NULL AS construction_brief")
    return ",\n    ".join(columns)


_FROM_WHERE = """
FROM project_temp_apply
LEFT JOIN system_dept
    ON system_dept.id = project_temp_apply.branch_id
LEFT JOIN system_users
    ON system_users.id = project_temp_apply.manager
WHERE
    project_temp_apply.STATUS = %(status)s
    AND project_temp_apply.create_time > %(create_time_after)s
"""


def query_apply_projects(
    page: int,
    page_size: int,
    settings: Optional[Settings] = None,
) -> tuple[list[dict[str, Any]], int]:
    """分页查询已申报成功的信息化项目。

    返回 (records, total)。
    """
    settings = settings or get_settings()
    brief_column = _safe_brief_column(settings.brief_column)

    params = {
        "status": settings.apply_status,
        "create_time_after": settings.create_time_after,
    }

    count_sql = f"SELECT COUNT(*) AS total {_FROM_WHERE}"
    select_sql = (
        f"SELECT\n    {_build_select_clause(brief_column)}{_FROM_WHERE}"
        "ORDER BY project_temp_apply.create_time DESC\n"
        "LIMIT %(limit)s OFFSET %(offset)s"
    )

    offset = (page - 1) * page_size
    list_params = dict(params, limit=page_size, offset=offset)

    conn = get_pool().connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(count_sql, params)
            total = int(cursor.fetchone()["total"])

            records: list[dict[str, Any]] = []
            if total > 0 and offset < total:
                cursor.execute(select_sql, list_params)
                records = list(cursor.fetchall())
    finally:
        conn.close()  # 归还连接到连接池

    return records, total


def ping() -> bool:
    """健康检查：确认数据库可连通。"""
    conn = get_pool().connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return True
    finally:
        conn.close()
