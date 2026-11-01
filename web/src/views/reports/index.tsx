import React, { useState } from 'react'
import { Card, Button, Space, Typography, message as Msg } from 'antd'
import { FileExcelOutlined, FileTextOutlined, DownloadOutlined } from '@ant-design/icons'
import { exportReport } from '@/api/reports'

const { Title, Paragraph } = Typography

const glass: React.CSSProperties = {
  background: 'rgba(18,26,46,0.55)',
  border: '1px solid rgba(255,255,255,0.08)',
  backdropFilter: 'blur(10px)',
}

const cards = [
  {
    key: 'compliance' as const,
    title: '等保合规报表',
    desc: '包含合规概览、资产合规明细（开放漏洞 / 严重高危 / 资产风险分 / 达标判定）与漏洞清单，用于等保测评与周期汇报。',
    icon: <FileTextOutlined style={{ fontSize: 28, color: '#13c2c2' }} />,
  },
  {
    key: 'vulnerabilities' as const,
    title: '漏洞清单导出',
    desc: '导出当前可见范围内的全部漏洞清单（含风险等级、状态、关联资产、端口与发现时间），便于离线分析与归档。',
    icon: <FileExcelOutlined style={{ fontSize: 28, color: '#1677ff' }} />,
  },
]

export default function ReportsPage() {
  const [loading, setLoading] = useState<string | null>(null)

  const handleExport = async (type: 'compliance' | 'vulnerabilities') => {
    setLoading(type)
    try {
      await exportReport(type)
      Msg.success('导出成功')
    } catch {
      Msg.error('导出失败，请重试')
    } finally {
      setLoading(null)
    }
  }

  return (
    <div style={glass} className="page-glass">
      <Title level={2} style={{ color: '#e6edf7', marginTop: 0 }}>合规与报表</Title>
      <Paragraph style={{ color: '#9fb0c9' }}>
        按数据范围导出安全合规报表，支持等保测评与漏洞治理归档。报表内容随当前账号权限范围过滤。
      </Paragraph>
      <Space direction="vertical" size={16} style={{ width: '100%', marginTop: 8 }}>
        {cards.map((c) => (
          <Card key={c.key} style={{ ...glass, borderRadius: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
              <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                {c.icon}
                <div>
                  <Title level={4} style={{ color: '#e6edf7', margin: 0 }}>{c.title}</Title>
                  <Paragraph style={{ color: '#9fb0c9', margin: '4px 0 0', maxWidth: 720 }}>{c.desc}</Paragraph>
                </div>
              </div>
              <Button type="primary" icon={<DownloadOutlined />} loading={loading === c.key}
                onClick={() => handleExport(c.key)}>
                导出 Excel
              </Button>
            </div>
          </Card>
        ))}
      </Space>
    </div>
  )
}
