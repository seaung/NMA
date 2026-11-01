# 安全说明（Security Policy）

NMA 是一套面向企业安全团队的漏洞闭环运营平台，涉及资产、漏洞、工单等敏感数据。本文档说明安全模型与部署加固建议。

## 支持的版本

| 版本 | 状态 |
| --- | --- |
| 1.x（main 分支） | 积极维护 |

## 报告安全漏洞

如发现安全漏洞，请**不要**在公开 Issue 中披露。请通过以下方式私信报告：

- 邮件：security@example.com（占位，部署方请替换为内部安全邮箱）
- 内部安全应急响应群 / 工单

我们将在收到报告后 5 个工作日内确认并评估影响范围，修复后在变更日志中说明（不公开漏洞细节）。

## 安全模型

- **认证**：基于 `djangorestframework-simplejwt` 的标准 JWT 流程（Access 30 分钟 / Refresh 7 天，可配置）。Refresh 轮换并写入黑名单（`token_blacklist`），登出即失效。
- **登录保护**：连续失败达到 `login_max_attempts`（默认 5 次）触发账户锁定 `account_lockout_minutes`（默认 30 分钟），计数基于缓存（建议生产使用 Redis）。
- **授权（RBAC）**：基于权限码（`Permission.code`）的接口级校验（`HasPermission`）。视图声明 `required_permissions`，超级管理员默认放行。
- **数据范围（行级权限）**：`get_data_scope` 依据角色 `data_scope`（`ALL` / `DEPT_AND_CHILD` / `DEPT` / `CUSTOM` / `SELF`）计算可见部门，列表/导出统一过滤。
- **权限缓存**：用户权限在 Redis（或本地缓存）中缓存，角色/权限/用户变更时通过 signal 失效。
- **密码策略**：使用 Django 默认 `MinimumLengthValidator`，生产建议增强。
- **限流**：DRF `DEFAULT_THROTTLE_RATES`（anon 60/min，user 600/min）。

## 部署加固清单

- [ ] 生产环境 `DJANGO_DEBUG=false`，切勿暴露 DEBUG 页面与栈追踪。
- [ ] 使用 **强随机** `DJANGO_SECRET_KEY`（≥32 字节，建议使用 `secrets.token_urlsafe(50)` 生成），并通过环境变量 / Secret 注入，**不要**提交到仓库或写入 `.env` 后入库。
- [ ] 通过 `CORS_ALLOWED_ORIGINS` 显式配置前端域名白名单，禁止使用 `*`。
- [ ] 数据库（PostgreSQL）、Redis、消息队列均启用认证与最小权限账号，禁止弱密码，网络层仅对必要端口放行。
- [ ] 反向代理（Nginx）启用 HTTPS（TLS 1.2+）、HSTS、安全响应头，并前置 WAF / 限流。
- [ ] Celery Broker 使用受密码保护的 Redis，并隔离内部网络。
- [ ] 定期更新依赖（`pip-audit` / `npm audit`），关注 Django、DRF、JWT、Ant Design 的安全公告。
- [ ] 备份 PostgreSQL 并演练恢复；敏感数据落盘（附件）应加密存储。

## 密钥与配置管理

- 所有机密通过环境变量注入（参考 `.env.example`），CI/CD 中使用平台 Secret。
- 演示账号（`admin / admin1234`、`secuser / sec1234`）**仅用于本地演示**，生产部署必须删除或重置强密码。
