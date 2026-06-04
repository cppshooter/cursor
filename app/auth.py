"""固定 KEY 认证。

客户端在请求头中携带固定 KEY（默认头名 X-API-Key）。
仅做简单的相等比对（使用常量时间比较避免计时攻击），不涉及其他认证逻辑。
"""

from __future__ import annotations

import hmac

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from .config import get_settings

_settings = get_settings()

# 通过配置的头名声明认证方案，OpenAPI 文档会自动展示「Authorize」入口。
_api_key_scheme = APIKeyHeader(
    name=_settings.api_key_header,
    auto_error=False,
    description="固定认证 KEY，请在请求头中携带。",
)


async def require_api_key(api_key: str | None = Depends(_api_key_scheme)) -> None:
    """校验请求头中的固定 KEY，不匹配则返回 401。"""
    expected = _settings.api_key
    if not api_key or not hmac.compare_digest(api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或缺失的认证 KEY",
            headers={"WWW-Authenticate": _settings.api_key_header},
        )
