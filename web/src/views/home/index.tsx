import React, { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Card, Row, Col, Statistic, Table, Timeline, Spin, Button, Tag, Empty, Space,
} from 'antd'
import {
  ClusterOutlined, BugOutlined, AlertOutlined, ThunderboltOutlined,
  WarningOutlined, SolutionOutlined, ReloadOutlined, FileTextOutlined,
} from '@ant-design/icons'
import { Area, Pie } from '@ant-design/charts'
import dayjs from 'dayjs'
import { getDashboard } from '@/api/dashboard'
import { RiskTag } from '@/components/StatusTag'
import type { DashboardData, RiskLevel } from '@/types'

const glass: React.CSSProperties = {
  background: 'rgba(18,26,46,0.55)',
  border: '1px solid rgba(255,255,255,0.08)',
  backdropFilter: 'blur(10px)',
}

const IMPORTANCE_LABEL: Record<number, string> = { 1: '低', 2: '中', 3: '高', 4: '核心' }

const metricsDef = [
  { key: 'asset_total', title: '资产总数', icon: <ClusterOutlined />, color: '#1677ff' },
  { key: 'vuln_total', title: '漏洞总数', icon: <BugOutlined />, color: '#ff4d4f' },
  { key: 'open_vuln_count', title: '待处理漏洞', icon: <AlertOutlined />, color: '#faad14' },
  { key: 'critical_high', title: '严重+高危', icon: <ThunderboltOutlined />, color: '#ff7a45' },
  { key: 'overdue_tickets', title: '逾期工单', icon: <WarningOutlined />, color: '#ff4d4f' },
  { key: 'open_tickets', title: '待办工单', icon: <SolutionOutlined />, color: '#13c2c2' },
] as const

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const load = async () => {
    setLoading(true)
    try {
      setData(await getDashboard())
    } finally {
      setLoading(false)
    }
  }
  useEffect(() => { load() }, [])

  const trendData = useMemo(() => {
    if (!data) return []
    return data.trend.flatMap((t) => [
      { date: t.date, value: t.discovered, type: '发现' },
      { date: t.date, value: t.fixed, type: '修复' },
    ])
  }, [data])

  const riskData = useMemo(() => {
    if (!data) return []
    const labelMap: Record<RiskLevel, string> = {
      critical: '严重', high: '高危', medium: '中危', low: '低危', info: '信息',
    }
    return data.vuln_by_risk.map((r) => ({ type: labelMap[r.level], value: r.count }))
  }, [data])

  const activities = useMemo(() => {
    if (!data) return []
    const v = data.recent_vulns.map((x) => ({
      time: x.discovered_at, color: 'red',
      text: `新漏洞「${x.name}」`, tag: <RiskTag level={x.risk_level} />,
    }))
    const t = data.recent_tickets.map((x) => ({
      time: x.created_at, color: 'blue',
      text: `工单「${x.title}」`, tag: <Tag color="cyan">{x.status}</Tag>,
    }))
    return [...v, ...t].sort((a, b) => (dayjs(b.time).isBefore(dayjs(a.time)) ? -1 : 1)).slice(0, 8)
  }, [data])

  const assetColumns = [
    { title: '资产', dataIndex: 'name', key: 'name', render: (n: string) => <a onClick={() => navigate('/assets')}>{n}</a> },
    { title: 'IP', dataIndex: 'ip', key: 'ip' },
    { title: '风险分', dataIndex: 'risk_score', key: 'risk_score', render: (v: number) => <b style={{ color: v >= 80 ? '#ff4d4f' : v >= 50 ? '#ff7a45' : '#faad14' }}>{v}</b> },
    { title: '等级', dataIndex: 'risk_level', key: 'risk_level', render: (l: RiskLevel) => <RiskTag level={l} /> },
    { title: '开放漏洞', dataIndex: 'open_vulns', key: 'open_vulns' },
    { title: '重要度', dataIndex: 'importance', key: 'importance', render: (i: number) => IMPORTANCE_LABEL[i] || i },
  ]

  return (
    <div style={glass} className="page-glass">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <h2 style={{ color: '#e6edf7', margin: 0 }}>安全运营总览</h2>
          <span style={{ color: '#9fb0c9', fontSize: 13 }}>资产暴露面 · 漏洞风险 · 工单处置 实时态势</span>
        </div>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={load}>刷新</Button>
          <Button type="primary" icon={<FileTextOutlined />} onClick={() => navigate('/reports')}>合规报表</Button>
        </Space>
      </div>

      <Spin spinning={loading}>
        <Row gutter={[16, 16]}>
          {metricsDef.map((m) => (
            <Col xs={12} sm={8} md={4} key={m.key}>
              <Card style={{ ...glass, borderRadius: 12 }}>
                <Statistic
                  title={<span style={{ color: '#9fb0c9' }}>{m.title}</span>}
                  value={data?.metrics[m.key as keyof DashboardData['metrics']] ?? 0}
                  prefix={React.cloneElement(m.icon, { style: { color: m.color } })}
                  valueStyle={{ color: m.color }}
                />
              </Card>
            </Col>
          ))}
        </Row>

        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} lg={16}>
            <Card title="漏洞发现 / 修复趋势（近 14 天）" style={{ ...glass, borderRadius: 12 }}>
              {data && trendData.length ? (
                <Area data={trendData} xField="date" yField="value" seriesField="type"
                  height={280} theme="dark" legend={{ position: 'top' }} />
              ) : <Empty description="暂无数据" />}
            </Card>
          </Col>
          <Col xs={24} lg={8}>
            <Card title="风险等级分布" style={{ ...glass, borderRadius: 12 }}>
              {data && riskData.length ? (
                <Pie data={riskData} angleField="value" colorField="type"
                  height={280} theme="dark" radius={0.92} innerRadius={0.55} legend={{ position: 'bottom' }} />
              ) : <Empty description="暂无数据" />}
            </Card>
          </Col>
        </Row>

        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} lg={14}>
            <Card title="Top 风险资产" style={{ ...glass, borderRadius: 12 }}>
              <Table rowKey="id" size="small" pagination={false}
                dataSource={data?.top_risk_assets || []} columns={assetColumns}
                locale={{ emptyText: <Empty description="暂无风险资产" /> }} />
            </Card>
          </Col>
          <Col xs={24} lg={10}>
            <Card title="最近动态" style={{ ...glass, borderRadius: 12 }}>
              {activities.length ? (
                <Timeline
                  items={activities.map((a) => ({
                    color: a.color,
                    children: (
                      <div style={{ color: '#e6edf7' }}>
                        <span style={{ marginRight: 8 }}>{a.text}</span>{a.tag}
                        <div style={{ color: '#9fb0c9', fontSize: 12 }}>{dayjs(a.time).format('MM-DD HH:mm')}</div>
                      </div>
                    ),
                  }))}
                />
              ) : <Empty description="暂无动态" />}
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  )
}
