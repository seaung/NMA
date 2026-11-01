import { useEffect, useState } from 'react'
import {
  Card, Table, Button, Input, Select, Space, Drawer, Form, Tag,
  Descriptions, Timeline, message as Msg, Row, Col,
} from 'antd'
import { PlusOutlined, SearchOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import {
  getTickets, getTicket, createTicket, assignTicket, transitionTicket, addComment,
} from '@/api/tickets'
import { getUsers } from '@/api/users'
import { getAssets } from '@/api/assets'
import { getVulnerabilities } from '@/api/vulnerabilities'
import type { Ticket, TicketStatus, TicketPriority } from '@/types'

const PRIORITY_COLOR: Record<TicketPriority, string> = { critical: 'red', high: 'volcano', medium: 'gold', low: 'blue' }
const PRIORITY_LABEL: Record<TicketPriority, string> = { critical: '严重', high: '高', medium: '中', low: '低' }
const STATUS_COLOR: Record<TicketStatus, string> = {
  created: 'default', assigned: 'blue', processing: 'orange', pending_verify: 'cyan',
  resolved: 'green', closed: 'default', rejected: 'red', reopened: 'purple',
}
const STATUS_LABEL: Record<TicketStatus, string> = {
  created: '已创建', assigned: '已分配', processing: '处理中', pending_verify: '待验证',
  resolved: '已解决', closed: '已关闭', rejected: '已拒绝', reopened: '重新打开',
}
const TRANSITIONS: Record<TicketStatus, TicketStatus[]> = {
  created: ['assigned', 'rejected', 'closed'],
  assigned: ['processing', 'rejected', 'closed'],
  processing: ['pending_verify', 'rejected', 'closed'],
  pending_verify: ['resolved', 'processing', 'closed'],
  resolved: ['closed', 'reopened'],
  closed: ['reopened'],
  rejected: ['created', 'closed'],
  reopened: ['processing', 'closed'],
}

const glass: React.CSSProperties = {
  background: 'rgba(18,26,46,0.55)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(10px)',
}

export default function TicketsPage() {
  const [data, setData] = useState<Ticket[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState({ search: '', status: undefined as TicketStatus | undefined, priority: undefined as TicketPriority | undefined, is_overdue: undefined as boolean | undefined })
  const [detail, setDetail] = useState<Ticket | null>(null)
  const [createOpen, setCreateOpen] = useState(false)
  const [form] = Form.useForm()
  const [userOptions, setUserOptions] = useState<{ value: number; label: string }[]>([])
  const [assetOptions, setAssetOptions] = useState<{ value: number; label: string }[]>([])
  const [vulnOptions, setVulnOptions] = useState<{ value: number; label: string }[]>([])
  const [txTarget, setTxTarget] = useState<TicketStatus | undefined>()
  const [txNote, setTxNote] = useState('')
  const [txRes, setTxRes] = useState('')
  const [assignId, setAssignId] = useState<number | undefined>()
  const [comment, setComment] = useState('')

  const fetchData = async (p = page) => {
    setLoading(true)
    try {
      const params: any = { page: p, page_size: 10 }
      if (filters.search) params.search = filters.search
      if (filters.status) params.status = filters.status
      if (filters.priority) params.priority = filters.priority
      if (filters.is_overdue !== undefined) params.is_overdue = String(filters.is_overdue)
      const res = await getTickets(params)
      setData(res.results)
      setTotal(res.count)
    } finally { setLoading(false) }
  }

  useEffect(() => { fetchData(1).then(() => setPage(1)) }, [])

  const openDetail = async (record: Ticket) => {
    const full = await getTicket(record.id)
    setDetail(full)
    setTxTarget(undefined); setTxNote(''); setTxRes(''); setAssignId(full.assignee || undefined); setComment('')
  }

  const refreshDetail = async () => {
    if (!detail) return
    setDetail(await getTicket(detail.id))
  }

  const doTransition = async () => {
    if (!detail || !txTarget) return
    await transitionTicket(detail.id, txTarget, txNote, txRes)
    Msg.success('状态已更新')
    await refreshDetail()
  }

  const doAssign = async () => {
    if (!detail || !assignId) return
    await assignTicket(detail.id, assignId)
    Msg.success('已分配')
    await refreshDetail()
  }

  const doComment = async () => {
    if (!detail || !comment.trim()) return
    await addComment(detail.id, comment)
    setComment('')
    Msg.success('评论已提交')
    await refreshDetail()
  }

  const openCreate = async () => {
    const [u, a, v] = await Promise.all([
      getUsers({ page: 1, page_size: 200 }),
      getAssets({ page: 1, page_size: 200 }),
      getVulnerabilities({ page: 1, page_size: 200 }),
    ])
    setUserOptions(u.results.map((x: any) => ({ value: x.id, label: x.nickname || x.username })))
    setAssetOptions(a.results.map((x: any) => ({ value: x.id, label: `${x.name}(${x.ip})` })))
    setVulnOptions(v.results.map((x: any) => ({ value: x.id, label: x.name })))
    form.resetFields(); form.setFieldsValue({ priority: 'medium', status: 'created' })
    setCreateOpen(true)
  }

  const onSubmit = async () => {
    const values = await form.validateFields()
    await createTicket(values)
    Msg.success('创建成功')
    setCreateOpen(false)
    fetchData(page)
  }

  const columns: ColumnsType<Ticket> = [
    { title: '标题', dataIndex: 'title', key: 'title' },
    { title: '优先级', dataIndex: 'priority', key: 'priority', render: (p) => <Tag color={PRIORITY_COLOR[p as TicketPriority]}>{PRIORITY_LABEL[p as TicketPriority]}</Tag> },
    { title: '状态', dataIndex: 'status', key: 'status', render: (s) => <Tag color={STATUS_COLOR[s as TicketStatus]}>{STATUS_LABEL[s as TicketStatus]}</Tag> },
    { title: '创建人', dataIndex: 'creator_name', key: 'creator_name' },
    { title: '处理人', dataIndex: 'assignee_name', key: 'assignee_name', render: (v) => v || '-' },
    { title: '截止时间', dataIndex: 'deadline', key: 'deadline', render: (v) => v || '-' },
    {
      title: 'SLA', key: 'sla', render: (_, r) => r.is_overdue
        ? <Tag color="red">已逾期</Tag>
        : <Tag color="green">正常</Tag>,
    },
    { title: '创建时间', dataIndex: 'created_at', key: 'created_at' },
    { title: '操作', key: 'action', render: (_, r) => <Button size="small" onClick={() => openDetail(r)}>详情</Button> },
  ]

  return (
    <div style={glass} className="page-glass">
      <Card title="工单管理" style={{ background: 'transparent', border: 'none' }}>
        <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
          <Col><Input allowClear placeholder="搜索标题" prefix={<SearchOutlined />} value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} onPressEnter={() => fetchData(1)} style={{ width: 220 }} /></Col>
          <Col><Select allowClear placeholder="状态" style={{ width: 130 }} options={(Object.keys(STATUS_LABEL) as TicketStatus[]).map((s) => ({ value: s, label: STATUS_LABEL[s] }))} value={filters.status} onChange={(v) => setFilters({ ...filters, status: v })} /></Col>
          <Col><Select allowClear placeholder="优先级" style={{ width: 120 }} options={(Object.keys(PRIORITY_LABEL) as TicketPriority[]).map((s) => ({ value: s, label: PRIORITY_LABEL[s] }))} value={filters.priority} onChange={(v) => setFilters({ ...filters, priority: v })} /></Col>
          <Col><Select allowClear placeholder="逾期" style={{ width: 100 }} value={filters.is_overdue} onChange={(v) => setFilters({ ...filters, is_overdue: v })} options={[{ value: true, label: '已逾期' }, { value: false, label: '未逾期' }]} /></Col>
          <Col><Button type="primary" onClick={() => fetchData(1)}>查询</Button></Col>
          <Col flex="auto" />
          <Col><Button icon={<PlusOutlined />} type="primary" onClick={openCreate}>新建工单</Button></Col>
        </Row>

        <Table rowKey="id" loading={loading} columns={columns} dataSource={data}
          pagination={{ total, current: page, pageSize: 10, showTotal: (t) => `共 ${t} 条`, onChange: (p) => { setPage(p); fetchData(p) } }}
          scroll={{ x: 1100 }} />
      </Card>

      <Drawer title="工单详情" width={620} open={!!detail} onClose={() => setDetail(null)} destroyOnClose>
        {detail && (
          <>
            <Descriptions column={1} size="small" bordered>
              <Descriptions.Item label="标题">{detail.title}</Descriptions.Item>
              <Descriptions.Item label="优先级"><Tag color={PRIORITY_COLOR[detail.priority]}>{PRIORITY_LABEL[detail.priority]}</Tag></Descriptions.Item>
              <Descriptions.Item label="状态"><Tag color={STATUS_COLOR[detail.status]}>{STATUS_LABEL[detail.status]}</Tag></Descriptions.Item>
              <Descriptions.Item label="创建人">{detail.creator_name}</Descriptions.Item>
              <Descriptions.Item label="处理人">{detail.assignee_name || '-'}</Descriptions.Item>
              <Descriptions.Item label="关联漏洞">{detail.vuln_name || '-'}</Descriptions.Item>
              <Descriptions.Item label="关联资产">{detail.asset_name || '-'}</Descriptions.Item>
              <Descriptions.Item label="截止时间">{detail.deadline || '-'}{detail.is_overdue && <Tag color="red" style={{ marginLeft: 8 }}>已逾期</Tag>}</Descriptions.Item>
              <Descriptions.Item label="解决方案">{detail.resolution || '-'}</Descriptions.Item>
            </Descriptions>

            <div style={{ margin: '16px 0' }}>
              <div style={{ marginBottom: 8, color: '#9fb0c9' }}>状态流转</div>
              <Space wrap>
                <Select style={{ width: 160 }} placeholder="目标状态" value={txTarget} onChange={setTxTarget}
                  options={TRANSITIONS[detail.status].map((s) => ({ value: s, label: STATUS_LABEL[s] }))} />
                <Input placeholder="流转备注" value={txNote} onChange={(e) => setTxNote(e.target.value)} style={{ width: 180 }} />
                {txTarget === 'resolved' && <Input placeholder="解决方案" value={txRes} onChange={(e) => setTxRes(e.target.value)} style={{ width: 180 }} />}
                <Button type="primary" disabled={!txTarget} onClick={doTransition}>提交流转</Button>
              </Space>
            </div>

            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8, color: '#9fb0c9' }}>指派处理人</div>
              <Space>
                <Select style={{ width: 200 }} placeholder="选择处理人" showSearch optionFilterProp="label" value={assignId} onChange={setAssignId} options={userOptions} />
                <Button onClick={doAssign}>分配</Button>
              </Space>
            </div>

            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 8, color: '#9fb0c9' }}>处理历史</div>
              <Timeline items={detail.histories.map((h) => ({
                color: 'blue',
                children: `${h.operator_name || '系统'} ${STATUS_LABEL[h.new_status as TicketStatus] || h.action}（${h.created_at}）${h.comment ? '：' + h.comment : ''}`,
              }))} />
            </div>

            <div>
              <div style={{ marginBottom: 8, color: '#9fb0c9' }}>评论（{detail.comments.length}）</div>
              {detail.comments.map((c) => (
                <div key={c.id} style={{ padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: 12, color: '#9fb0c9' }}>{c.author_name} · {c.created_at}</div>
                  <div>{c.content}</div>
                </div>
              ))}
              <Input.TextArea rows={2} placeholder="输入评论" value={comment} onChange={(e) => setComment(e.target.value)} style={{ marginTop: 8 }} />
              <Button type="primary" style={{ marginTop: 8 }} onClick={doComment}>提交评论</Button>
            </div>
          </>
        )}
      </Drawer>

      <Drawer title="新建工单" width={520} open={createOpen} onClose={() => setCreateOpen(false)} destroyOnClose
        extra={<Space><Button onClick={() => setCreateOpen(false)}>取消</Button><Button type="primary" onClick={onSubmit}>保存</Button></Space>}>
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="工单标题" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="description" label="描述"><Input.TextArea rows={3} /></Form.Item>
          <Form.Item name="priority" label="优先级" rules={[{ required: true }]}><Select options={(Object.keys(PRIORITY_LABEL) as TicketPriority[]).map((s) => ({ value: s, label: PRIORITY_LABEL[s] }))} /></Form.Item>
          <Form.Item name="status" label="初始状态"><Select options={[{ value: 'created', label: '已创建' }, { value: 'assigned', label: '已分配' }]} /></Form.Item>
          <Form.Item name="assignee" label="处理人"><Select allowClear showSearch optionFilterProp="label" options={userOptions} /></Form.Item>
          <Form.Item name="vulnerability" label="关联漏洞"><Select allowClear showSearch optionFilterProp="label" options={vulnOptions} /></Form.Item>
          <Form.Item name="asset" label="关联资产"><Select allowClear showSearch optionFilterProp="label" options={assetOptions} /></Form.Item>
        </Form>
      </Drawer>
    </div>
  )
}
