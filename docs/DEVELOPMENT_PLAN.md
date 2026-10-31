# NMA 漏洞運營管理系統 — 改進方案與開發週期

> 對標「抖象科技」級別的漏洞運營管理平台。
> 技術棧：Django 5 + DRF + SimpleJWT + Celery(manager: Redis) + PostgreSQL 後端；
> React 18 + Vite + Ant Design 5 + Redux Toolkit + React Router 6 前端。

---

## 一、現況盤點（2026-10-31）

### 已具備
| 模塊 | 狀態 |
|---|---|
| 用戶模型（AbstractUser + 部門/角色/權限/菜單） | ✅ 模型完整 |
| 主機資產 `HostAssets`、IT 資產 `Assets` | ✅ 模型完整 |
| 主機/ Web 漏洞模型（基類抽象） | ✅ 模型完整 |
| 漏洞工單 + 歷史 + 評論 | ✅ 模型完整；工單 API（分配/狀態流轉/評論）已寫 |
| 掃描任務 + 日誌模型 | ✅ 模型完整（Celery 執行端未有） |
| 站內消息 + 系統配置模型 | ✅ 模型完整（API 未寫） |
| JWT 登入/登出、角色/部門/菜單管理 API | ✅ 已寫但**未接線到 urls** |
| 前端骨架（登入頁、Layout、403/404/500、路由懶加載） | ✅ 已搭 |

### 主要問題（按嚴重度）
1. **資料庫仍是 sqlite3**，且 `postgresql` 驅動、連接層根本未生效（settings 沒接環境變數）。
2. **模型註冊不完整**：`app/models/__init__.py` 只導出 `Users`，其餘 15+ 個模型 Django 看不見，無法建遷移。
3. **API 接線缺失**：`api/v1/urls.py` 只有 `user/login`，資產/工單/角色/部門/菜單路由都沒註冊。
4. **多處代碼級 Bug**：
   - `users/views.py`：`Departments`/`Menu` 未 import 卻直接使用；`DepartmentsViewSets.retrieve` 重複定義且邏輯錯誤；`RolesViewSets` 缺 `queryset`/`serializer_class`；`update` 方法簽名與基類不符。
   - `users/views.py` 密碼修改：調用 `validated_data('new_password')`（應為取下標）；序列化器字段（old_password/new_password）與視圖期望（password）不一致。
   - `assets/views.py`：`queryset.filter(department=user.department)` 誤把 `dept` 寫成 `department`；訪問匿名 `user.department` 會炸。
   - 前端 `request.ts`：`localstorage`（應為 `localStorage`）；`get/post` 返回裸 axios 而非攔截器實例。
5. **遷移債**：僅 2 個舊 migration 覆蓋舊模型集，與現模型嚴重脫節。
6. **工程化缺失**：`docker-compose.yml` 為空、`.env` 機制沒有、無 seeding 命令、無測試、Redis 未部署。

---

## 二、改進方案總覽

### A. 基建（原則：一切配置可從 .env 讀取）
- `settings.py`：python-dotenv + `.env`；默認 PostgreSQL（nma 庫）；時區 Asia/Shanghai；CORS 放開（開發期）；DRF/SIMPLE_JWT 統一配置。
- `docker-compose.yml` 補齊：postgres + redis + web/backend 服務（開發自舉）。
- 統一回應結構 + 統一異常處理器（`libs/renderers` 已有骨架）。

### B. 後端 API 補全
| 模塊 | 接口集 |
|---|---|
| 用戶 | 登入/登出/改密/個人信息/CRUD |
| RBAC | 角色/部門/菜單/權限 CRUD + 用戶-角色分配 |
| 資產 | 主機資產 CRUD + 標籤/篩選/批量導入；IT 資產 CRUD |
| 漏洞 | 主機/ Web 漏洞 CRUD、狀態流轉、一鍵生成工單 |
| 工單 | 完整狀態機 + 歷史 + 評論（已有 80%） |
| 任務 | 任務 CRUD + Celery 觸發 + 進度輪詢 |
| 消息 | 站內信收發/未讀數 |

### C. 前端補全
- 修復 axios 攔截器；登入態 Redux store + 路由守衛。
- 動態菜單（後端菜單表驅動）+ Layout 側邊欄。
- 各業務模塊列表/表單頁（Antd ProTable 風格）+ Dashboard 圖表。

### D. 掃描引擎（對標抖象的核心差異點）
- python-nmap 包裝：主機發現 → 端口/服務指紋 → 版本/CVE 匹配 → 入庫/生成漏洞。
- Celery 隊列拆分（scan / notify / report），beat 定時掃描，任務進度落庫。

---

## 三、開發週期（Phase 與里程碑）

| 階段 | 內容 | 產出驗收標準 |
|---|---|---|
| **P1 後端地基**（本階段） | 切換 PostgreSQL；模型全量註冊 + 重建遷移；路由全面接線；修復阻斷性 Bug；種子數據命令；登入冒煙測試 | `check` 0 錯誤；`migrate` 全量成功；seeder 可用；登入 API 返回 JWT |
| **P2 登入閉環 + 前端骨架** | 修 request.ts；Redux auth store；登入/登出/路由守衛；動態菜單；Layout | 瀏覽器完整登入體驗；菜單由後端菜單表驅動 |
| **P3 核心業務 API** | 資產/漏洞/工單/用戶管理 CRUD 補全 + 分頁/篩選/統一回應格式；pytests 覆蓋核心接口 | `pytest` 全綠；接口文檔（drf-spectacular）可導出 |
| **P4 掃描引擎** | nmap 包裝 Celers 任務、進度輪詢、結果觸發漏洞/工單聯動；Redis 就緒 | 手動觸發掃描localhost成功；漏洞自動入庫 |
| **P5 統計與報表** | Dashboard 聚合接口、圖表頁、報表導出（openpyxl） | 儀表盤可用、Excel 導出正確 |
| **P6 加固與交付** |（持續） | 環境分離 settings、"docker-compose up" 一鍵起全棧、安全項（限流/審計/密碼策略）、CI | compose 一鍵部署；測試/CI 綠 |

各階段獨立可交付，向後兼容；順序不變動。

---

## 四、第一階段（P1）執行清單 —— ✅ 已完成（2026-10-31）
1. ✅ 環境檢測：Python 3.14（venv，Django 5.2.18）/ PostgreSQL 18.6（postgres/123456，`nma` 庫）就緒。
2. ✅ `settings.py` 接 `.env` 切換 PostgreSQL，時區/語言/CORS/JWT/DRF 配置；`NMAX/.env.example` 提供。
3. ✅ `app/models/__init__.py` 註冊全部 16 個模型；修復 `assets.py` 字符串引用（`users.Users` → `app.Users`）。
4. ✅ `api/v1/urls.py` 全面接線（DefaultRouter 註冊 users/roles/departments/menus/assets/tickets + login/logout）。
5. ✅ 修復 views 阻斷 Bug：`Users` import、重複/錯誤 `retrieve`、`validated_data()` 調用誤用、`user.department`→`dept` 等；舊遷移清理重建為 `0001_initial`。
6. ✅ `manage.py seed_data`（admin/Admin@123456 + 2 部門 + 3 角色）；冒煙測試全過：登入返回 JWT、4 個業務接口 200、無 token 401、錯密碼 400。

**驗收證據**：`migrate` 全量 OK；`POST /api/v1/user/login` 200 返回 token；`GET /api/v1/{roles,departments,tickets,assets}` 均 200。
