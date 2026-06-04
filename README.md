# 信息化项目申报查询 API

一个独立的、符合 RESTful 规范的只读 API 服务，用于查询**已申报成功**的信息化项目信息。

- 基于 FastAPI 构建，自带交互式 API 文档（Swagger UI / ReDoc）。
- 数据直接来自指定 MySQL 服务器的给定 SQL。
- 带分页信息；**只读**，不暴露任何写操作。
- 使用一个**固定 KEY** 做简单认证（请求头携带），不做其他认证。

## 返回字段

| 字段                 | 说明         | 来源                              |
| -------------------- | ------------ | --------------------------------- |
| `project_name`       | 项目名称     | `project_temp_apply.name`         |
| `declare_dept`       | 申报单位     | `system_dept.name`                |
| `construction_brief` | 建设简介内容 | 见下方「关于建设简介内容」        |
| `contact_person`     | 联系人       | `system_users.nickname`           |
| `contact_phone`      | 联系电话     | `project_temp_apply.manager_phone`|
| `declare_time`       | 申报时间     | `project_temp_apply.create_time`  |

底层查询与需求中给定的 SQL 一致（状态值与时间过滤已参数化）：

```sql
SELECT
    project_temp_apply.name,
    system_dept.name,
    system_users.nickname,
    project_temp_apply.manager_phone,
    project_temp_apply.create_time
FROM project_temp_apply
LEFT JOIN system_dept
    ON system_dept.id = project_temp_apply.branch_id
LEFT JOIN system_users
    ON system_users.id = project_temp_apply.manager
WHERE
    project_temp_apply.STATUS = 'check_doing'
    AND project_temp_apply.create_time > '2024-05-31 00:00:00';
```

### 关于建设简介内容

需求要求返回「建设简介内容」，但给定 SQL 中并未包含对应列，且表结构未知。
因此该字段默认返回 `null`。若数据库中确实存在该列（例如 `content` / `remark` /
`build_content` 等），只需在环境变量 `BRIEF_COLUMN` 中填写真实列名，服务会自动将其
纳入查询并返回。列名会做合法性校验以防注入。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制示例文件并按实际情况修改：

```bash
cp .env.example .env
# 编辑 .env，填入数据库连接信息与你的固定 API_KEY
```

也可直接通过系统环境变量配置（优先级高于 `.env`）。

### 3. 启动服务

```bash
python -m app.main
# 或
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

启动后访问：

- 交互式文档：<http://localhost:8000/docs>
- ReDoc 文档：<http://localhost:8000/redoc>
- 健康检查：<http://localhost:8000/health>

## 接口说明

### `GET /api/v1/project-applies`

分页查询已申报成功的信息化项目。

**认证**：请求头携带固定 KEY（默认头名 `X-API-Key`）。

**查询参数**：

| 参数        | 类型 | 默认 | 说明                     |
| ----------- | ---- | ---- | ------------------------ |
| `page`      | int  | 1    | 页码，从 1 开始          |
| `page_size` | int  | 10   | 每页条数（默认上限 100） |

**请求示例**：

```bash
curl -H "X-API-Key: please-change-this-key" \
  "http://localhost:8000/api/v1/project-applies?page=1&page_size=10"
```

**响应示例**：

```json
{
  "meta": {
    "page": 1,
    "page_size": 10,
    "total": 42,
    "total_pages": 5
  },
  "items": [
    {
      "project_name": "某信息化建设项目",
      "declare_dept": "某某局",
      "construction_brief": null,
      "contact_person": "张三",
      "contact_phone": "13800000000",
      "declare_time": "2024-06-01T10:00:00"
    }
  ]
}
```

**状态码**：

- `200` 查询成功
- `401` KEY 缺失或错误
- `422` 分页参数非法
- `503` 数据库查询失败

### `GET /health`

无需认证的健康检查，返回服务与数据库连通状态。

## 安全说明

- 认证仅为「固定 KEY 简单比对」（常量时间比较），请通过环境变量配置足够复杂的
  `API_KEY`，并在生产环境置于 HTTPS（反向代理）之后。
- 服务为纯只读，SQL 中的状态值、时间过滤、分页参数均参数化，避免 SQL 注入。
