# NMA 漏洞运营管理系统

面向企业安全团队的漏洞闭环运营平台：资产暴露面盘点 → 漏洞发现/验证/修复/复测/关闭 → 工单流转 → 扫描任务 → 看板与合规报表。对标企业级漏洞运营系统（斗象科技内部运营产品能力）。

## 技术栈

- 后端：Django 5.2 LTS + DRF 3.16 + SimpleJWT 5.5、PostgreSQL 16、Redis 7、Celery 5.4 + django-celery-beat、drf-spectacular、openpyxl、python-nmap
- 前端：React 18 + Vite 5 + Ant Design 5 + Redux Toolkit
- 工程化：ruff、pytest/pytest-django/factory-boy、tsc/eslint、GitHub Actions CI、Docker Compose

## 目录结构

```
NMA/
├── NMAX/                 # Django 后端
│   ├── app/
│   │   ├── configs/      # 配置（base/dev/prod）、urls、celery、wsgi/asgi
│   │   ├── models/       # 领域模型（users/assets/vulnerabilities/tasks/workflow/system）
│   │   ├── api/v1/       # DRF 路由与视图（auth/users/assets/vulnerabilities/tickets...）
│   │   ├── libs/         # 统一响应/异常/分页/权限
│   │   ├── services/     # 业务规则（状态机/评分/扫描引擎）—— 后续周次补充
│   │   ├── selectors/    # 查询与数据范围 —— 后续周次补充
│   │   └── management/commands/seed_demo.py  # 演示数据初始化
│   ├── requirements.txt
│   └── Dockerfile
├── web/                  # React 前端
├── docker-compose.yml
└── README.md
```

## 环境要求

- Python 3.12+（推荐用 uv 管理虚拟环境）
- PostgreSQL 16+，Redis 7+
- Node 20+（前端）

## 本地启动（后端）

```bash
cd NMAX
uv venv --python 3.12 .venv
uv pip install -r requirements.txt
cp .env.example .env            # 按需修改数据库/密钥
# 创建数据库（若使用本机 PostgreSQL）
#   createdb -h 127.0.0.1 -U postgres -E UTF8 nma
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

API 文档：`http://127.0.0.1:8000/api/docs/`，Schema：`/api/schema/`，健康检查：`/health/`。
认证默认管理员：`admin / admin1234`，安全工程师：`secuser / sec1234`。

## 本地启动（前端）

```bash
cd web
yarn install
yarn dev                          # http://localhost:3000
```

## Docker 启动（生产/一体化）

```bash
# 仅起基础依赖（本地开发后端直连）
docker compose up -d redis postgres

# 全栈（含 backend + frontend 镜像）
docker compose up -d --build
```

## 测试

```bash
# 后端（需可用 PostgreSQL；pytest-django 会创建 test_<DB> 库）
cd NMAX
.venv/bin/python -m pytest -q --cov=app --cov-report=term-missing

# 静态检查
.venv/bin/ruff check .

# 前端
cd web
npm ci
npm run lint      # ESLint（0 error，any 降级为 warning）
npm run build     # tsc -b 类型检查 + Vite 构建
npm run typecheck # tsc -b 类型检查
```

> CI：`.github/workflows/ci.yml` 在 push/PR 到 `main` 时自动运行后端（PostgreSQL + Redis 服务 + ruff + pytest 覆盖率）与前端（lint + build）。

## 权限矩阵（RBAC）

默认角色与数据范围：

| 角色 | 数据范围 | 权限码 |
| --- | --- | --- |
| 管理员 `admin` | 全部（ALL） | 全部：`asset:*` `vuln:*` `ticket:*` `task:*` `report:*` `user:*` `role:manage` `dept:manage` `menu:manage` `perm:manage` `system:view` |
| 安全工程师 `security` | 本部门及以下（DEPT_AND_CHILD） | `asset:view/manage` `vuln:view/manage` `ticket:view/manage` `task:view/manage` `report:view/export` |

权限码通过视图 `required_permissions` 强制校验；列表/导出按 `data_scope` 过滤可见数据。自定义角色可在「系统管理」中配置数据范围与权限。

## 安全

- 认证：SimpleJWT（Access 30min / Refresh 7d，可配），Refresh 轮换并黑名单，登出即失效。
- 登录失败锁定（`login_max_attempts` / `account_lockout_minutes`，基于缓存）。
- 授权：接口级 `HasPermission` + 行级数据范围；权限 Redis 缓存并在角色/权限/用户变更时失效。
- 生产务必 `DJANGO_DEBUG=false`、使用强随机 `DJANGO_SECRET_KEY`、显式配置 `CORS_ALLOWED_ORIGINS`。
- 详见 [SECURITY.md](./SECURITY.md)。

## 已完成进度

- **第 1 周 基线**：模型层收敛、配置拆分、迁移重建、登出黑名单、docker 与 `seed_demo`。
- **第 2 周 认证/RBAC**：`/auth/{login,refresh,logout,me,password}`、`HasPermission` + 数据范围、前端 auth store/守卫/Layout。
- **第 3–4 周 资产/漏洞**：暴露面模型与 API、漏洞状态机/去重/导入导出、前端资产与漏洞页。
- **第 5 周 工单/消息**：工单流转/SLA/评论/历史、站内消息、前端工单与消息页。
- **第 6 周 扫描**：Celery/Redis、`ScanEngine` 接口 + Nmap、任务 API/执行/日志、前端任务页。
- **第 7 周 风险/报表**：风险评分模型、Dashboard 统计/趋势/Top 资产、合规报表导出、前端看板与报表。
- **第 8 周 测试/CI**：pytest（factory-boy + API 测试、覆盖率）、ruff、前端 lint/build 门禁、GitHub Actions CI、SECURITY.md。

## 后续周次

第 9 周：修 bug、补运维手册与权限矩阵、上线演练。
