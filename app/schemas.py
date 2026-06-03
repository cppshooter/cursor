"""响应数据模型（Pydantic）。"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjectApplyItem(BaseModel):
    """单条已申报成功的信息化项目记录。"""

    project_name: Optional[str] = Field(None, description="项目名称")
    declare_dept: Optional[str] = Field(None, description="申报单位")
    construction_brief: Optional[str] = Field(None, description="建设简介内容")
    contact_person: Optional[str] = Field(None, description="联系人")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    declare_time: Optional[datetime] = Field(None, description="申报时间")


class PageMeta(BaseModel):
    """分页信息。"""

    page: int = Field(..., description="当前页码，从 1 开始")
    page_size: int = Field(..., description="每页条数")
    total: int = Field(..., description="符合条件的记录总数")
    total_pages: int = Field(..., description="总页数")


class ProjectApplyPage(BaseModel):
    """分页查询结果。"""

    meta: PageMeta
    items: list[ProjectApplyItem]
