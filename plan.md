NMA 漏洞運營管理系統：現狀評估、改進方案與開發週期
0. 結論
目前專案是「可編譯但不可端到端運行」的早期骨架：後端已有使用者、角色、資產、漏洞、工單、任務、消息等模型雛形；前端已有登錄頁、Layout 與首頁。但資料庫仍是空 SQLite、Migration 未落地、多數 Model 未註冊、API 只有登錄一個路由，前端請求位址與後端不一致，且缺少權限、測試、部署與文件。

建議節奏：第 1 週修復基線，第 2～6 週完成 MVP，第 7～8 週加固與上線，第 9 週緩衝。單人全端約 9 週；兩人並行可壓縮到 5～6 週。

1. 目標與成功標準
1.1 產品目標
建立一套可實際運營的漏洞閉環系統：

資產管理：主機、Web、域名、網絡設備等資產統一盤點。
漏洞管理：手工錄入、批量導入、掃描發現、去重、驗證、修復、複測、關閉、風險接受。
工單流轉：漏洞自動/手動轉工單，指派、處理、驗證、關閉，保留完整歷史。
任務與掃描：即時/定時掃描任務，Celery 異步執行，日誌與結果可追溯。
通知與看板：站內消息、逾期提醒、漏洞趨勢、風險資產排行、修復率/MTTR。
權限與審計：角色、選單、操作權限、資料範圍、審計日誌。
工程化：PostgreSQL、Redis、環境變數、Docker、測試、CI、API 文件。
1.2 驗收標準
全新環境執行 docker compose up -d 後，可完成 migrate、seed_demo、登錄。
登錄 → 首頁看板 → 新增資產 → 新增/導入漏洞 → 轉工單 → 指派 → 修復 → 複測 → 關閉，全流程可用。
不同角色只能看到授權範圍內的資料；越權 API 返回 403。
後端 pytest 全綠，核心模組覆蓋率 ≥ 70%；前端 tsc、eslint、build 全綠。
README 可讓新成員在 30 分鐘內跑起專案；/api/docs/ 可查看完整 API。
CI 在 PR 上自動執行後端測試與前端檢查。
1.3 本期不做
多租戶、SSO/LDAP、計費。
Nessus、AWVS、Burp 等商業掃描器深度對接（先預留 ScanEngine 介面）。
移動端 App、複雜報表設計器。
2. 現狀評估（已實際檢查）
區域	現況	影響
資料庫	settings.py 仍用 SQLite；NMAX/app/db.sqlite3 為 0 bytes；showmigrations 顯示所有 Migration 未套用	專案從未真正建庫，無法登錄或保存資料
PostgreSQL	本機 5432 已運行，postgres/123456 可連接；但未安裝 psycopg/psycopg2，也沒有 nma_db	無法切換到指定的 PostgreSQL
Migration	0002 將 Users.roles 建成 ForeignKey，但 Model 是 ManyToManyField；makemigrations --check 還會生成 0003	Migration 與 Model 不一致，重建庫必失敗
Model 註冊	models/init.py 只導出 Users；實測只註冊了 Users/Roles/Departments/Permission/Menu 五個模型	資產、漏洞、工單、任務、消息、系統配置完全沒進 Django 模型層
路由	api/v1/urls.py 只有 user/login；assets/workflow 的 ViewSet 從未掛載	前端除了登錄沒有可用 API
後端錯誤	users/views.py 使用 Departments、Menu 但未 import；update 中 serializer.validated_data('new_password') 是錯誤呼叫；assets/views.py 使用不存在的 user.department	執行到即 500
認證	auth.py 自定義 JWT 驗證邏輯不正確且未啟用；RefreshToken.blacklist() 需要 token_blacklist app 但未安裝；自建黑名單表明文存 token	登出、刷新、失效控制都不可靠
帳號模型	nickname 必填且唯一，但建立使用者的 Serializer 只收 username/password；email 未唯一；created_at 使用 auto_now 而非 auto_now_add	建使用者會 IntegrityError；時間欄位會每次 save 被改寫
前端請求	request.ts 的 axios instance 定義了但匯出的是原生 axios；localstorage 拼寫錯誤；後端是 /api/v1，前端登錄卻打 /api/login；未配置 Vite Proxy	登錄必定失敗，所有請求繞過攔截器
前端認證	login/index.tsx 登錄成功後沒有保存 token、沒有跳轉；路由沒有守衛；Layout 選單是靜態的	無法進入受保護頁面，無權限控制
前端品質	npx tsc -b 有 3 個錯誤，eslint 有 3 個 error；@ant-design/icons 未顯式列入 dependencies	無法穩定構建
工程化	docker-compose.yml 為空；README.md 只有兩行；無測試、無 CI、無 .env、無 API 文件	無法部署、無法協作、無法回歸
補充：本機 Redis 未啟動，但 Docker 可用；PostgreSQL 有 collation version mismatch 警告，不影響開發，必要時執行 ALTER DATABASE ... REFRESH COLLATION VERSION。

3. 總體架構決策
3.1 後端保持單一 Django app，按領域分層
不拆成多個 Django app，避免 migration label、AppConfig、迴圈引用與 import 路徑重構成本。保留 app app，內部按領域組織：

代码块


NMAX/app/
├── configs/
│   ├── settings/{base,dev,prod}.py
│   ├── urls.py
│   ├── celery.py
│   ├── asgi.py / wsgi.py
├── models/
│   ├── accounts/      # Users, Roles, Departments, Permission, Menu, AuditLog
│   ├── assets/        # Asset
│   ├── vulnerabilities/ # Vulnerability, VulnerabilityAsset, History, Attachment
│   ├── workflow/      # Ticket, TicketHistory, TicketComment
│   ├── tasks/         # Task, TaskLog, ScanResult
│   ├── notifications/ # Message, MessageRecipient
│   └── system/        # SystemConfig
├── api/v1/
│   ├── auth/ users/ assets/ vulnerabilities/ tickets/ tasks/
│   ├── messages/ dashboard/ system/
│   └── urls.py
├── services/          # 業務規則、狀態機、掃描適配器
├── selectors/         # 查詢與資料範圍
├── libs/              # 權限、分頁、渲染器、異常處理
└── management/commands/seed_demo.py
3.2 重建 Migration
目前 DB 為空、Migration 從未套用，直接重置是最乾淨的方案：

刪除 NMAX/app/migrations/0001_initial.py、0002_*.py。
修正所有 Model 後執行 makemigrations app，產生新的 0001_initial.py。
在 PostgreSQL nma_db 上執行 migrate。
刪除 0 bytes 的 NMAX/app/db.sqlite3（已被 .gitignore 忽略，無資料損失）。
假設：目前沒有任何有價值的資料。若你另有 SQLite 資料，請在執行前先備份並改為資料遷移方案。

3.3 技術棧版本
Python：用 uv 建立 Python 3.12 虛擬環境（本機已安裝 uv）。目前 .venv 是 Python 3.14，Django 5.0 對 3.14 的支援不完整。
Django：5.2 LTS；DRF 3.16；SimpleJWT 5.5。
PostgreSQL：16+，驅動用 psycopg[binary]。
Redis：7+，Celery broker/result backend + 快取。
前端維持 React 18 + Vite 5 + Ant Design 5 + Redux Toolkit，不在此期升級 React 19。
3.4 API 契約
統一使用前端已假設的 envelope：

json


{
  "code": 0,
  "msg": "success",
  "data": {}
}
code=0 成功；1001 參數錯誤；1002 未認證；1003 無權限；1004 不存在；5000 伺服器錯誤。
HTTP status 仍保持正確（400/401/403/404/500）。
分頁資料放在 data 內：{count, next, previous, results}。
全域 Exception Handler 統一轉換 DRF ValidationError、PermissionDenied、NotFound、JWT 例外。
4. 後端改進方案
4.1 配置與依賴
更新 requirements.txt：

Django>=5.2,<5.3
djangorestframework>=3.16
djangorestframework-simplejwt>=5.5
psycopg[binary]>=3.2
django-cors-headers
django-filter
drf-spectacular
celery[redis]>=5.4
redis>=5
django-celery-beat
python-nmap
python-dotenv
openpyxl（導入/導出 Excel）
gunicorn
pytest, pytest-django, factory-boy, ruff
設定拆分：

configs/settings/base.py：共用設定。
configs/settings/dev.py：DEBUG=True、本機 Postgres/Redis、CORS 
http://localhost:3000
、Media 本地存放。
configs/settings/prod.py：從環境變數讀取、DEBUG=False、ALLOWED_HOSTS 白名單、HTTPS/Secure Cookie、日誌。
.env.example 提交，.env 忽略。
manage.py、wsgi.py、asgi.py、celery.py 統一讀 DJANGO_SETTINGS_MODULE=app.configs.settings.dev。
關鍵設定：

python


DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": env("DB_NAME", "nma_db"),
    "USER": env("DB_USER", "postgres"),
    "PASSWORD": env("DB_PASSWORD", "123456"),
    "HOST": env("DB_HOST", "127.0.0.1"),
    "PORT": env("DB_PORT", "5432"),
    "CONN_MAX_AGE": 60,
  }
}
INSTALLED_APPS 加入 rest_framework_simplejwt.token_blacklist、corsheaders、django_filters、drf_spectacular、django_celery_beat。
MIDDLEWARE 加入 corsheaders.middleware.CorsMiddleware。
REST_FRAMEWORK：預設 JWTAuthentication、IsAuthenticated、DjangoFilterBackend、SearchFilter、OrderingFilter、統一 Renderer/ExceptionHandler、分頁、節流。
SIMPLE_JWT：access 30 分鐘、refresh 7 天、ROTATE_REFRESH_TOKENS=True、BLACKLIST_AFTER_ROTATION=True。
CACHES 使用 Redis；CELERY_BROKER_URL/RESULT_BACKEND 使用 Redis。
LANGUAGE_CODE="zh-hans"、TIME_ZONE="Asia/Shanghai"、USE_TZ=True。
MEDIA_URL/MEDIA_ROOT、STATIC_ROOT。
DEFAULT_AUTO_FIELD 保持 BigAutoField。
4.2 資料模型重構
帳號與權限
Users：移除重複的 password 欄位；nickname 改為 blank=True（或建立時自動用 username）；email 加 unique=True；新增 phone、avatar、password_changed_at；created_at 改 auto_now_add；updated_at 保持 auto_now；自訂 Manager 支援 create_user/create_superuser。
Departments：新增 code（unique）、sort；owner 改為 FK Users（可空）；parent 保留；時間欄位修正。
Roles：name 加 unique；保留 code、role_type、data_scope、enable、menus、departments、permissions。
Permission：保留 name/code/type/parent/api_path/method；加唯一約束。
Menu：新增 component、icon、sort、permission（FK 可空）；保留 path/menu_type/parent/visible。
新增 AuditLog：user、action、resource_type、resource_id、before、after、ip、user_agent、created_at。
移除 TokenDisbacklistReacord，改用 SimpleJWT token_blacklist 的 OutstandingToken/BlacklistedToken。
資產
將 HostAssets 重命名/升級為 Asset，移除現有兩個資產模型並存的設計（assets.py 與 host_assets.py）。
欄位：name、ip（unique）、hostname、asset_type、asset_status、area、manager（FK Users）、department（FK Departments）、business_system、os_type、os_version、kernel_version、mac_address、dns_server、gateway、cpu_model、cpu_cores、memory_size、disk_size、is_hardened、security_level、tags（JSON）、description、last_scan_time、created_by、created_at、updated_at、is_deleted、deleted_at。
加索引：ip、asset_type、department、security_level、is_deleted。
漏洞
合併 HostVulnerability 與 WebVulnerability 為單一 Vulnerability + VulnerabilityAsset，避免雙表重複與報表分裂。
Vulnerability 欄位：name、description、cve_id、cnnvd_id、source（manual/scan/import）、vuln_type、risk_level、cvss_score、status、impact、solution、poc、verify_info、fingerprint（可空、用於去重）、sla_due_at、discovered_at、verified_at、fixed_at、closed_at、created_by、created_at、updated_at、is_deleted、deleted_at。
Web 證據欄位：affected_url、request_method、request_header、request_body、response_header、response_body；主機欄位：affected_component、affected_version、affected_port、protocol。可空，按類型填寫。
VulnerabilityAsset：vulnerability、asset、component、version、port、protocol、evidence；unique_together=("vulnerability","asset")。
VulnerabilityHistory：記錄狀態變更、操作人、備註。
VulnerabilityAttachment：附件、上傳人、建立時間。
狀態枚舉：unverified、verified、fixing、pending_retest、fixed、closed、false_positive、risk_accepted。
風險等級排序改用整數映射（critical=4/high=3/medium=2/low=1/info=0），避免 -risk_level 字母排序錯誤。
工單
VulnerabilityTicket 增加 vulnerability FK（PROTECT 或 SET_NULL）、asset FK、department FK、closed_at。
保留 TicketHistory、TicketComment；新增附件可選。
狀態：created、assigned、processing、pending_verify、resolved、closed、rejected、reopened。
任務與掃描
Task：creator 保持 FK；asset_id 改為 assets M2M；新增 targets JSON（域名/URL/子網）、scan_config JSON、schedule_type（once/cron/interval）、cron_expression、interval_seconds、progress、result_summary、celery_task_id。
TaskLog 保持；新增 ScanResult 保存原始掃描輸出，便於追溯。
掃描器用 ScanEngine 介面封裝：MVP 實作 NmapScanEngine，後續可接其他引擎。
通知與系統配置
Message：新增 level、link、sender 可空（系統消息）、expires_at。
MessageRecipient：保留已讀/刪除狀態，加 (message, recipient) 唯一約束。
SystemConfig：改為純 key-value（key unique、value JSON/text、description、is_system），移除表中固定的 session_timeout 等欄位；這些值改由系統預設 + DB 覆蓋。
新增 LoginAttempt 或使用 Redis 計數實現登錄鎖定。
4.3 認證與權限
使用 SimpleJWT 標準流程：/auth/login/、/auth/refresh/、/auth/logout/、/auth/me/、/auth/password/。
登錄成功更新 last_login_ip、last_login_time；回傳使用者資訊、角色、權限、選單。
登出用 refresh token blacklist；access token 生命週期縮短至 30 分鐘，避免需要即時撤銷 access 的複雜度。
登錄失敗計數 + 鎖定：沿用 SystemConfig.max_login_attempts/account_lockout_duration，用 Redis 計數，成功登錄清零。
HasPermission 修正：
required_permissions 支援列表與 |/& 組合。
超級管理員直接通過。
權限快取使用 Redis，並在 Role/Permission/User 變更時透過 signal 清除。
新增 has_object_permission，資產/漏洞/工單按負責人、部門校驗。
資料範圍 helper：
python


def scope_queryset(user, queryset, dept_field="department", owner_field="created_by"):
    # ALL / DEPT_AND_CHILD / DEPT / SELF / CUSTOM
多角色取聯集；CUSTOM 使用 role.departments；SELF 用建立人或負責人。
4.4 API 設計
全部掛在 /api/v1/，使用 DRF Router + ViewSet；列表統一支援 page/page_size/search/ordering 與領域篩選。

模組	端點
認證	POST /auth/login/、POST /auth/refresh/、POST /auth/logout/、GET/PATCH /auth/me/、PUT /auth/password/
使用者	GET/POST /users/、GET/PUT/DELETE /users/{id}/、POST /users/{id}/reset-password/
角色	GET/POST /roles/、GET/PUT/DELETE /roles/{id}/、PUT /roles/{id}/permissions/
部門	GET/POST /departments/、GET/PUT/DELETE /departments/{id}/、GET /departments/tree/
選單/權限	GET/POST /menus/、GET /menus/tree/、GET /permissions/
資產	GET/POST /assets/、GET/PUT/DELETE /assets/{id}/、POST /assets/import/、GET /assets/export/、POST /assets/{id}/scan/
漏洞	GET/POST /vulnerabilities/、GET/PUT/DELETE /vulnerabilities/{id}/、POST /vulnerabilities/import/、GET /vulnerabilities/export/、POST /vulnerabilities/{id}/transition/、GET /vulnerabilities/statistics/
工單	GET/POST /tickets/、GET/PUT /tickets/{id}/、POST /tickets/{id}/assign/、POST /tickets/{id}/transition/、GET/POST /tickets/{id}/comments/、GET /tickets/{id}/history/
任務	GET/POST /tasks/、GET/PUT/DELETE /tasks/{id}/、POST /tasks/{id}/run/、POST /tasks/{id}/cancel/、GET /tasks/{id}/logs/
消息	GET /messages/、POST /messages/{id}/read/、POST /messages/read-all/、GET /messages/unread-count/
看板	GET /dashboard/summary/、GET /dashboard/trend/、GET /dashboard/top-assets/、GET /dashboard/ticket-stats/
系統	GET/PUT /system/configs/、GET /audit-logs/
文件	GET /api/schema/、GET /api/docs/、GET /health/
4.5 狀態機與業務規則
漏洞狀態流轉（由 service 強制校驗，不允許前端直接改 status）：

代码块


unverified -> verified | false_positive
verified   -> fixing | risk_accepted
fixing     -> pending_retest
pending_retest -> fixed | verified（複測失敗退回）
fixed      -> closed
closed     -> verified（重新打開）
risk_accepted -> verified（取消接受）
工單流轉：

代码块


created -> assigned -> processing -> pending_verify -> resolved -> closed
created/assigned/processing -> rejected
resolved/closed -> reopened -> assigned
規則：

每次流轉寫入 TicketHistory/VulnerabilityHistory，記錄操作人、前後狀態、備註。
resolved 必須填寫 resolution；verified 必須有驗證資訊。
依風險等級計算 SLA：critical 24h、high 72h、medium 7d、low 30d；可由 SystemConfig 覆蓋。
逾期漏洞/工單在列表與看板標紅，並產生站內通知。
刪除使用軟刪除（Asset/Vulnerability），保留歷史與審計。
4.6 Celery 與掃描
補齊 configs/celery.py，設定 app.autodiscover_tasks()、時區、序列化、重試。
任務：
run_scan_task(task_id)：校驗目標必須是系統內資產/授權網段；呼叫 ScanEngine；更新 Task.status/progress；寫 TaskLog/ScanResult。
sync_scan_results(task_id)：解析結果，按 fingerprint 去重，建立/更新 Vulnerability 與 VulnerabilityAsset。
notify_overdue()：每日掃描逾期漏洞/工單並發消息。
django-celery-beat 管理定時任務；前端建立任務時寫入週期配置。
安全限制：生產環境只允許掃描資產庫內目標；禁止任意 URL/IP；掃描前記錄審計日誌；設定逾時與併發上限。
開發環境沒有 Redis 時，提供 CELERY_TASK_ALWAYS_EAGER=True 開關，方便測試。
4.7 測試與品質
pytest.ini + conftest.py，測試資料庫使用 PostgreSQL（與生產一致）。
必測：
認證：登錄、刷新、登出、過期、黑名單、鎖定。
權限：五種 data_scope、角色聯集、物件級越權。
資產/漏洞 CRUD、批量導入、去重、狀態機非法流轉。
工單指派/流轉/SLA/評論/歷史。
任務執行（mock ScanEngine）、日誌、失敗重試。
Dashboard 聚合數字與 DB 一致。
覆蓋率目標：核心模組 ≥ 70%，整體 ≥ 60%。
啟用 ruff 格式與 lint；API schema 由 drf-spectacular 自動生成。
5. 前端改進方案
5.1 基礎設施
vite.config.ts 加 Proxy：
ts


server: {
  port: 3000,
  proxy: {
    '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true }
  }
}
.env.development：VITE_API_BASE_URL=/api/v1
package.json 補 @ant-design/icons、dayjs、@types/node 已在；新增 typecheck script。
刪除 CRA 預設樣式 src/App.css、src/index.css 中的全域按鈕/連結樣式，改用 AntD ConfigProvider + zhCN。
5.2 請求與認證
重寫 request.ts 為 src/api/http.ts：
使用同一個 axios instance。
Request interceptor 注入 Authorization: Bearer <access>。
Response interceptor 解包 {code,msg,data}；code!==0 統一 message.error。
401 時用 refresh token 換新 access，排隊重放請求；refresh 失敗清 token 並跳 /login。
src/utils/token.ts：存取/清除 access、refresh、user。
src/store/：
authSlice：user、permissions、menus、isAuthenticated。
uiSlice：collapsed、theme。
使用 typed hooks，登錄成功後寫入 store + localStorage。
src/router/：
公開路由：/login、403/404/500。
ProtectedRoute：未登錄跳登錄；無權限跳 403。
路由表集中管理，與選單權限碼對應。
Layout：
選單從 /auth/me 回傳的 menus 生成，或使用前端靜態路由表 + 權限過濾。
選中項與當前路徑同步；支援折疊、麵包屑。
Header 顯示真實使用者、角色；登出呼叫 /auth/logout/ 並清 store。
5.3 頁面
頁面	功能
登錄	呼叫 /auth/login/，保存 token/user，跳轉首頁；錯誤提示
首頁看板	資產總數、漏洞總數/嚴重度分佈、待處理、逾期、趨勢圖、Top 風險資產、最近動態（全部接真實 API）
資產管理	列表（分頁/搜尋/篩選）、新增/編輯 Drawer、詳情（基本資訊/漏洞/掃描記錄）、導入、導出
漏洞管理	列表（嚴重度/狀態/資產/來源篩選）、詳情（證據/POC/影響/修復建議/歷史）、新增/編輯、批量導入、狀態流轉按鈕
工單管理	列表/看板、建立工單、指派、流轉、評論、歷史、逾期標記
任務管理	列表、建立掃描任務、執行/取消、進度、日誌、結果
系統管理	使用者、角色、部門、選單、權限、系統配置、審計日誌
消息中心	列表、已讀/全部已讀、未讀角標
錯誤頁	403/404/500 保持現有元件，接入路由
5.4 共用元件與型別
src/types/：User、Role、Asset、Vulnerability、Ticket、Task、Message、Paginated。
src/api/：按領域拆 API 模組，禁止在頁面直接寫 axios。
共用元件：
PageContainer：標題、麵包屑、操作區。
SearchTable：AntD Table + 查詢表單 + 分頁封裝。
RiskTag、StatusTag、PriorityTag。
PermissionButton：依權限碼顯示/禁用。
ImportModal、ExportButton、EmptyState、ErrorBoundary。
表單校驗與後端錯誤碼對應；列表空狀態、載入態、錯誤態完整。
前端測試：Vitest + React Testing Library 覆蓋 token、http、權限 hook；可選 Playwright 做登錄→建資產→建漏洞 smoke。
6. 資料庫與環境落地步驟
建立資料庫（本機）：
bash


PGPASSWORD=123456 createdb -h 127.0.0.1 -U postgres -E UTF8 nma_db
建立 .env（不提交）：
dotenv


DJANGO_SETTINGS_MODULE=app.configs.settings.dev
SECRET_KEY=dev-only-change-me
DEBUG=True
DB_NAME=nma_db
DB_USER=postgres
DB_PASSWORD=123456
DB_HOST=127.0.0.1
DB_PORT=5432
REDIS_URL=redis://127.0.0.1:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:3000
用 uv 重建 Python 3.12 環境：
bash


uv venv --python 3.12 .venv
uv pip install -r requirements.txt
重置 Migration 並建表：
bash


cd NMAX
../.venv/bin/python manage.py makemigrations app
../.venv/bin/python manage.py migrate
../.venv/bin/python manage.py seed_demo
啟動 Redis（本機沒有 redis-server，用 Docker）：
bash


docker compose up -d redis postgres
啟動後端與前端：
bash


cd NMAX && ../.venv/bin/python manage.py runserver 0.0.0.0:8000
cd web && yarn dev
在 docker-compose.yml 補齊：
postgres:16（volume、healthcheck、nma_db）
redis:7
backend（Gunicorn + migrate 入口）
frontend（Nginx 靜態檔案 + /api 反向代理）
更新 README.md：環境需求、安裝、啟動、測試、目錄結構、常見問題、API 文件入口。
7. 開發週期（單人全端，9 週）
週次	階段	主要交付	驗收標準
第 1 週	基線修復	settings 拆分、Postgres/Redis、依賴、Migration 重建、登錄 E2E、Docker Compose、README	全新環境可 migrate + seed + 登錄；check 無錯
第 2 週	認證與 RBAC	JWT 登錄/刷新/登出/me、使用者/角色/部門/選單/權限 API、資料範圍、前端 auth store/guard/layout	不同角色登錄後看到不同選單；越權 403
第 3～4 週	資產與漏洞	Asset/Vulnerability 模型與 API、導入/導出、去重、狀態機、前端列表/詳情/表單、首頁基礎統計	資產→漏洞→驗證→修復全流程可操作
第 5 週	工單與通知	工單模型/API、指派/流轉/SLA、評論/歷史、站內消息、前端工單頁與消息中心	漏洞轉工單→指派→處理→驗證→關閉
第 6 週	任務與掃描	Celery/Redis、掃描任務、Nmap 適配器、任務日誌、定時任務、前端任務頁	建立掃描任務→執行→產生漏洞→日誌可查
第 7 週	報表與系統管理	Dashboard 完整統計、趨勢/排行、導出、系統配置、審計日誌、使用者管理 UI	看板數字與 DB 一致；配置可生效
第 8 週	測試與加固	後端測試、前端檢查、CI、權限矩陣、安全加固、效能、部署文件、UAT	pytest/tsc/eslint/build 全綠；UAT 通過
第 9 週	緩衝	修 bug、補文件、上線演練	可交付
里程碑：

M1（第 2 週末）：可登錄、可管理使用者與權限。
M2（第 4 週末）：資產與漏洞 MVP 可用。
M3（第 6 週末）：工單、通知、掃描任務可用，達到內部試用標準。
M4（第 8 週末）：測試、CI、部署完成，達到上線標準。
兩人並行建議：

後端工程師：第 1～8 週負責模型/API/權限/Celery/測試。
前端工程師：第 1 週基礎設施，第 2 週 auth/layout，第 3～7 週頁面，第 8 週聯調與 E2E。
可壓縮至 5～6 週，但需提前凍結 API 契約，並在第 2 週末完成介面定義。
8. 優先級與範圍控制
P0（MVP 必須）
PostgreSQL + 環境配置 + Migration 重建。
JWT 認證、使用者/角色/部門/選單、資料範圍。
資產 CRUD、漏洞 CRUD/導入/狀態機。
工單指派/流轉/歷史。
首頁基礎統計。
前端登錄、路由守衛、Layout、上述頁面。
Docker Compose + README。
P1（上線前應有）
Celery 掃描任務與日誌。
站內消息與逾期通知。
導入/導出 Excel。
審計日誌、系統配置。
Dashboard 趨勢/排行/MTTR。
測試與 CI。
P2（後續迭代）
Nessus/AWVS/Burp 掃描器接入。
SSO/LDAP、多租戶。
高級報表設計器、自定義欄位。
資產分組/憑證管理、自動化修復編排。
移動端。
9. 風險與假設
資料安全：目前 SQLite 為 0 bytes、Migration 未套用，重置 Migration 安全；若你另有資料，需先備份並改為資料遷移。
憑證安全：postgres/123456 只放本機 .env，不提交 Git；上線前更換強密碼並限制來源 IP。
Python 版本：目前 .venv 是 3.14，Django 5.0 支援不完整；計畫改用 uv 的 Python 3.12 + Django 5.2 LTS。若你堅持 3.14，需改採 Django 6.0 並重新驗證依賴。
Redis 未啟動：本機沒有 redis-server，需用 Docker 啟動；否則 Celery 與快取不可用。
PostgreSQL collation 警告：目前不影響連線；若後續出現排序/索引問題，執行 ALTER DATABASE nma_db REFRESH COLLATION VERSION。
掃描合規：掃描功能必須限制在授權資產/網段內，生產環境關閉任意目標輸入，避免法律與安全風險。
範圍蔓延：第 6 週末凍結 MVP 功能；P2 功能不進入本期，避免延期。
10. 最終交付物
可運行的 Django + PostgreSQL + Redis + Celery 後端。
React + Ant Design 前端，覆蓋登錄、看板、資產、漏洞、工單、任務、消息、系統管理。
全新 0001_initial Migration、seed_demo 初始化命令。
.env.example、docker-compose.yml、README.md、API 文件 /api/docs/。
後端 pytest 測試、前端 typecheck/lint/build、GitHub Actions CI。
一份權限矩陣與運維手冊（備份、部署、掃描安全限制、常見故障）。