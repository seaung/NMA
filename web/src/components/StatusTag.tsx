import { Tag } from 'antd'
import type { RiskLevel, VulnStatus, AssetStatus, SecurityLevel } from '@/types'

const RISK_COLOR: Record<RiskLevel, string> = {
  critical: 'red',
  high: 'volcano',
  medium: 'gold',
  low: 'blue',
  info: 'default',
}

const RISK_LABEL: Record<RiskLevel, string> = {
  critical: '严重',
  high: '高危',
  medium: '中危',
  low: '低危',
  info: '信息',
}

const VULN_STATUS_COLOR: Record<VulnStatus, string> = {
  unverified: 'default',
  verified: 'blue',
  fixing: 'orange',
  pending_retest: 'cyan',
  fixed: 'green',
  closed: 'default',
  false_positive: 'default',
  risk_accepted: 'purple',
}

const VULN_STATUS_LABEL: Record<VulnStatus, string> = {
  unverified: '未验证',
  verified: '已验证',
  fixing: '修复中',
  pending_retest: '待复测',
  fixed: '已修复',
  closed: '已关闭',
  false_positive: '误报',
  risk_accepted: '风险接受',
}

const ASSET_STATUS_COLOR: Record<AssetStatus, string> = {
  in_use: 'green',
  idle: 'default',
  maintenance: 'orange',
  scrapped: 'red',
}

const ASSET_STATUS_LABEL: Record<AssetStatus, string> = {
  in_use: '使用中',
  idle: '闲置',
  maintenance: '维护中',
  scrapped: '已报废',
}

const SECURITY_LABEL: Record<SecurityLevel, string> = {
  critical: '严重',
  high: '高危',
  medium: '中危',
  low: '低危',
  info: '信息',
}

export function RiskTag({ level }: { level: RiskLevel | SecurityLevel | null | undefined }) {
  if (!level) return <Tag>未知</Tag>
  return <Tag color={RISK_COLOR[level as RiskLevel]}>{RISK_LABEL[level as RiskLevel]}</Tag>
}

export function VulnStatusTag({ status }: { status: VulnStatus }) {
  return (
    <Tag color={VULN_STATUS_COLOR[status]}>{VULN_STATUS_LABEL[status]}</Tag>
  )
}

export function AssetStatusTag({ status }: { status: AssetStatus }) {
  return (
    <Tag color={ASSET_STATUS_COLOR[status]}>{ASSET_STATUS_LABEL[status]}</Tag>
  )
}

export { RISK_LABEL, VULN_STATUS_LABEL, ASSET_STATUS_LABEL, SECURITY_LABEL }
