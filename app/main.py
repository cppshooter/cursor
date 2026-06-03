"""信息化项目申报查询 API 服务（只读 RESTful）。

特性：
- 仅提供查询能力（只读），不暴露任何写操作。
- 固定 KEY 认证（请求头携带）。
- 数据来自给定 MySQL 的指定 SQL，带分页信息。
"""

from __future__ import annotations

import math

from fastapi import Depends, FastAPI, HTTPException, Query, status

from .auth import require_api_key
from .config import get_settings
from .db import ping, query_apply_projects
from .schemas import PageMeta, ProjectApplyItem, ProjectApplyPage

settings = get_settings()

app = FastAPI(
    title="信息化项目申报查询 API",
    description=(
        "查询已申报成功（状态为申报中/审核中）的信息化项目信息，只读接口，"
        "需在请求头携带固定 KEY 认证。"
    ),
    version="1.0.0",
)


@app.get("/health", tags=["系统"], summary="健康检查")
async def health() -> dict:
    """无需认证的存活探针；同时尝试探测数据库连通性。"""
    db_ok = False
    try:
        db_ok = ping()
    except Exception:  # noqa: BLE001 - 健康检查不抛出，仅反映状态
        db_ok = False
    return {"status": "ok", "database": "up" if db_ok else "down"}


@app.get(
    "/api/v1/project-applies",
    response_model=ProjectApplyPage,
    tags=["项目申报"],
    summary="分页查询已申报成功的信息化项目",
    dependencies=[Depends(require_api_key)],
)
async def list_project_applies(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(
        settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description=f"每页条数（最大 {settings.max_page_size}）",
    ),
) -> ProjectApplyPage:
    """返回项目名称、申报单位、建设简介内容、联系人、申报时间等字段，带分页。"""
    try:
        records, total = query_apply_projects(page=page, page_size=page_size)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据查询失败: {exc}",
        ) from exc

    total_pages = math.ceil(total / page_size) if total else 0
    return ProjectApplyPage(
        meta=PageMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
        items=[ProjectApplyItem(**row) for row in records],
    )


def run() -> None:
    """便于通过 `python -m app.main` 直接启动。"""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run()
