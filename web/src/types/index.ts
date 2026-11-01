// 全局类型定义

export type AssetType = 'host' | 'web' | 'domain' | 'network' | 'database' | 'other'
export type AssetStatus = 'in_use' | 'idle' | 'maintenance' | 'scrapped'
export type SecurityLevel = 'critical' | 'high' | 'medium' | 'low' | 'info'

export interface Asset {
  id: number
  name: string
  ip: string
  hostname: string
  domain: string
  ports: number[] | string[]
  web_url: string
  service_fingerprint: string
  exposed: boolean
  asset_group: string
  asset_type: AssetType
  asset_status: AssetStatus
  area: string
  importance: number
  security_level: SecurityLevel | null
  manager: number | null
  department: number | null
  business_system: string
  os_type: string
  os_version: string
  is_hardened: boolean
  tags: string[]
  description: string
  last_scan_time: string | null
  created_by: number | null
  created_at: string
  updated_at: string
}

export type RiskLevel = 'critical' | 'high' | 'medium' | 'low' | 'info'
export type VulnStatus =
  | 'unverified'
  | 'verified'
  | 'fixing'
  | 'pending_retest'
  | 'fixed'
  | 'closed'
  | 'false_positive'
  | 'risk_accepted'
export type VulnSource = 'manual' | 'scan' | 'import' | 'intel'

export interface VulnAssetLink {
  id: number
  asset: number
  asset_name: string
  asset_ip: string
  component: string
  version: string
  port: string
  protocol: string
  evidence: string
}

export interface VulnHistory {
  id: number
  operator: number | null
  operator_name: string
  old_status: VulnStatus | null
  new_status: VulnStatus | null
  note: string
  created_at: string
}

export interface Vulnerability {
  id: number
  name: string
  description: string
  cve_id: string | null
  cnnvd_id: string | null
  source: VulnSource
  vuln_type: string
  risk_level: RiskLevel
  cvss_score: number | null
  status: VulnStatus
  impact: string
  solution: string
  poc: string
  verify_info: string
  fingerprint: string | null
  sla_due_at: string | null
  discovered_at: string
  verified_at: string | null
  fixed_at: string | null
  closed_at: string | null
  affected_url: string
  request_method: string
  request_header: string
  request_body: string
  response_header: string
  response_body: string
  affected_component: string
  affected_version: string
  affected_port: string
  protocol: string
  created_by: number | null
  created_by_name: string
  created_at: string
  updated_at: string
  assets: VulnAssetLink[]
  histories: VulnHistory[]
  asset_ids: number[]
  risk_score: number
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export type TicketPriority = 'critical' | 'high' | 'medium' | 'low'
export type TicketStatus =
  | 'created' | 'assigned' | 'processing' | 'pending_verify'
  | 'resolved' | 'closed' | 'rejected' | 'reopened'

export interface TicketHistory {
  id: number
  operator: number
  operator_name: string
  action: string
  old_status: TicketStatus | null
  new_status: TicketStatus | null
  comment: string
  created_at: string
}

export interface TicketComment {
  id: number
  author: number
  author_name: string
  content: string
  created_at: string
}

export interface Ticket {
  id: number
  title: string
  description: string
  priority: TicketPriority
  status: TicketStatus
  creator: number
  creator_name: string
  assignee: number | null
  assignee_name: string | null
  department: number | null
  department_name: string | null
  vulnerability: number | null
  vuln_name: string | null
  asset: number | null
  asset_name: string | null
  deadline: string | null
  closed_at: string | null
  resolution: string | null
  status_display: string
  priority_display: string
  is_overdue: boolean
  histories: TicketHistory[]
  comments: TicketComment[]
  created_at: string
  updated_at: string
}

export type MessageType = 'system' | 'ticket' | 'vulnerability' | 'task' | 'overdue' | 'other'
export type MessageLevel = 'info' | 'warning' | 'danger'

export interface MessageItem {
  id: number
  message_id: number
  title: string
  content: string
  message_type: MessageType
  priority: string
  level: MessageLevel
  link: string
  message_created_at: string
  is_read: boolean
  read_time: string | null
}

export type TaskType = 'immediate' | 'scheduled' | 'periodic' | 'scan'
export type TaskStatus = 'pending' | 'running' | 'success' | 'failed' | 'timeout' | 'canceled'
export type TaskEngine = 'nmap' | 'nessus' | 'awvs' | 'custom'
export type TaskPriority = 'high' | 'medium' | 'low'

export interface TaskLog {
  id: number
  status: TaskStatus
  start_time: string
  end_time: string | null
  duration: number | null
  result: string | null
  error_message: string | null
  created_at: string
}

export interface ScanResultItem {
  id: number
  raw_output: string
  parsed: Record<string, any>[]
  created_at: string
}

export interface Task {
  id: number
  name: string
  description: string | null
  task_type: TaskType
  task_type_display: string
  status: TaskStatus
  status_display: string
  priority: TaskPriority
  priority_display: string
  engine: TaskEngine
  engine_display: string
  assets: number[]
  assets_detail: { id: number; name: string; ip: string }[]
  targets: string[]
  target_type: string | null
  scan_config: Record<string, any>
  scan_ports: string | null
  schedule_type: string
  cron_expression: string | null
  progress: number
  result_summary: string
  error_message: string | null
  celery_task_id: string | null
  creator: number
  creator_name: string
  timeout: number
  created_at: string
  updated_at: string
  logs: TaskLog[]
  scan_results: ScanResultItem[]
}

export interface DashboardMetrics {
  asset_total: number
  vuln_total: number
  open_vuln_count: number
  fixed_vuln_count: number
  critical_high: number
  open_tickets: number
  overdue_tickets: number
}

export interface TrendPoint {
  date: string
  discovered: number
  fixed: number
}

export interface AssetRiskItem {
  id: number
  name: string
  ip: string
  security_level: SecurityLevel | null
  importance: number
  risk_score: number
  risk_level: RiskLevel
  open_vulns: number
}

export interface RecentVuln {
  id: number
  name: string
  risk_level: RiskLevel
  status: VulnStatus
  discovered_at: string
}

export interface RecentTicket {
  id: number
  title: string
  priority: string
  status: string
  created_at: string
}

export interface DashboardData {
  metrics: DashboardMetrics
  vuln_by_risk: { level: RiskLevel; count: number }[]
  vuln_by_status: { status: VulnStatus; count: number }[]
  trend: TrendPoint[]
  top_risk_assets: AssetRiskItem[]
  recent_vulns: RecentVuln[]
  recent_tickets: RecentTicket[]
}
