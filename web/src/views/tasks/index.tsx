import { useEffect, useState } from 'react'
import {
  Card, Table, Button, Input, Select, Space, Drawer, Form, Tag, Progress,
  Popconfirm, Timeline, Descriptions, message as Msg, Row, Col, Tabs, Empty, Spin,
} from 'antd'
import { PlusOutlined, SearchOutlined, PlayCircleOutlined, StopOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import {
  getTasks, getTask, createTask, deleteTask, runTask, cancelTask,
} from '@/api/tasks'
import { getAssets } from '@/api/assets'
import { RiskTag } from '@/components/StatusTag'
import type { Task, TaskStatus, TaskEngine, TaskType, TaskPriority } from '@/types'

const STATUS_COLOR: Record<TaskStatus, string> = {
  pending: 'default', running: 'processing', success: 'green', failed: 'red', timeout: 'volcano', canceled: 'default',
}
const STATUS_LABEL: Record<TaskStatus, string> = {
  pending: '等待执行', running: '执行中', success: '执行成功', failed: '执行失败', timeout: '执行超时', canceled: '已取消',
}
const ENGINE_LABEL: Record<TaskEngine, string> = { nmap: 'Nmap', nessus: 'Nessus', awvs: 'AWVS', custom: '自定义' }
const TYPE_LABEL: Record<TaskType, string> = { immediate: '即时任务', scheduled: '定时任务', periodic: '周期任务', scan: '扫描任务' }
const PRIORITY_COLOR: Record<TaskPriority, string> = { high: 'red', medium: 'gold', low: 'blue' }
const PRIORITY_LABEL: Record<TaskPriority, string> = { high: '高', medium: '中', low: '低' }

const glass: React.CSSProperties = {
  background: 'rgba(18,26,46,0.55)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(10px)',
}

const parseTargets = (text?: string): string[] =>
  (text || '').split(/[\n,，\s]+/).map((s) => s.trim()).filter(Boolean)

export default function TasksPage() {
  const [data, setData] = useState<Task[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState({ search: '', status: undefined as TaskStatus | undefined, engine: undefined as TaskEngine | undefined })
  const [detail, setDetail] = useState<Task | null>(null)
  const [createOpen, setCreateOpen] = useState(false)
  const [form] = Form.useForm()
  const [assetOptions, setAssetOptions] = useState<{ value: number; label: string }[]>([])

  const fetchData = async (p = page) => {
    setLoading(true)
    try {
      const params: any = { page: p, page_size: 10 }
      if (filters.search) params.search = filters.search
      if (filters.status) params.status = filters.status
      if (filters.engine) params.engine = filters.engine
      const res = await getTasks(params)
      setData(res.results)
      setTotal(res.count)
    } finally { setLoading(false) }
  }

  useEffect(() => { fetchData(1).then(() => setPage(1)) }, [])

  // 执行中任务自动轮询进度
  useEffect(() => {
    if (detail && detail.status === 'running') {
      const t = setInterval(async () => {
        const fresh = await getTask(detail.id)
        setDetail(fresh)
      }, 2000)
      return () => clearInterval(t)
    }
  }, [detail?.status, detail?.id])

  const openDetail = async (id: number) => { setDetail(await getTask(id)) }

  const onRun = async (record: Task) => {
    await runTask(record.id)
    Msg.success('已触发执行')
    openDetail(record.id)
    fetchData(page)
  }
  const onCancel = async (record: Task) => {
    await cancelTask(record.id)
    Msg.success('已取消')
    fetchData(page)
  }

  const openCreate = async () => {
    const res = await getAssets({ page: 1, page_size: 200 })
    setAssetOptions(res.results.map((a: any) => ({ value: a.id, label: `${a.name}(${a.ip})` })))
    form.resetFields(); form.setFieldsValue({ engine: 'nmap', task_type: 'scan', priority: 'medium', scan_ports: '1-1000' })
    setCreateOpen(true)
  }
  const onSubmit = async () => {
    const v = await form.validateFields()
    const payload = { ...v, targets: parseTargets(v.targets) }
    await createTask(payload)
    Msg.success('创建成功')
    setCreateOpen(false)
    fetchData(page)
  }

  const columns: ColumnsType<Task> = [
    { title: '任务名称', dataIndex: 'name', key: 'name' },
    { title: '引擎', dataIndex: 'engine', key: 'engine', render: (e) => <Tag color="blue">{ENGINE_LABEL[e as TaskEngine]}</Tag> },
    { title: '类型', dataIndex: 'task_type', key: 'task_type', render: (t) => TYPE_LABEL[t as TaskType] },
    { title: '优先级', dataIndex: 'priority', key: 'priority', render: (p) => <Tag color={PRIORITY_COLOR[p as TaskPriority]}>{PRIORITY_LABEL[p as TaskPriority]}</Tag> },
    {
      title: '状态', key: 'status', render: (_, r) => (
        <div>
          <Tag color={STATUS_COLOR[r.status]}>{STATUS_LABEL[r.status]}</Tag>
          {r.status === 'running' && <Progress percent={r.progress} size="small" style={{ width: 120, marginTop: 4 }} />}
        </div>
      ),
    },
    { title: '进度', dataIndex: 'progress', key: 'progress', render: (v) => `${v}%` },
    { title: '创建人', dataIndex: 'creator_name', key: 'creator_name' },
    { title: '创建时间', dataIndex: 'created_at', key: 'created_at' },
    {
      title: '操作', key: 'action', render: (_, r) => (
        <Space>
          {r.status !== 'running' && <Button size="small" type="primary" icon={<PlayCircleOutlined />} onClick={() => onRun(r)}>执行</Button>}
          {r.status === 'running' && <Button size="small" danger icon={<StopOutlined />} onClick={() => onCancel(r)}>取消</Button>}
          <Button size="small" onClick={() => openDetail(r.id)}>详情</Button>
          <Popconfirm title="确认删除？" onConfirm={async () => { await deleteTask(r.id); Msg.success('已删除'); fetchData(page) }}>
            <Button size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const renderDetail = () => {
    if (!detail) return null
    const latest = detail.scan_results[0]
    const findings = latest?.parsed || []
    return (
      <>
        <Descriptions column={1} size="small" bordered>
          <Descriptions.Item label="名称">{detail.name}</Descriptions.Item>
          <Descriptions.Item label="引擎">{ENGINE_LABEL[detail.engine]}</Descriptions.Item>
          <Descriptions.Item label="状态"><Tag color={STATUS_COLOR[detail.status]}>{STATUS_LABEL[detail.status]}</Tag></Descriptions.Item>
          <Descriptions.Item label="进度"><Progress percent={detail.progress} /></Descriptions.Item>
          <Descriptions.Item label="目标">{(detail.targets || []).join('、') || '-'}</Descriptions.Item>
          <Descriptions.Item label="关联资产">{detail.assets_detail.map((a) => <Tag key={a.id}>{a.name}</Tag>) || '-'}</Descriptions.Item>
          <Descriptions.Item label="结果摘要">{detail.result_summary || '-'}</Descriptions.Item>
          {detail.error_message && <Descriptions.Item label="错误信息"><span style={{ color: '#ff4d4f' }}>{detail.error_message}</span></Descriptions.Item>}
        </Descriptions>

        <Tabs style={{ marginTop: 16 }} items={[
          {
            key: 'logs', label: '执行日志',
            children: detail.logs.length ? (
              <Timeline items={detail.logs.map((l) => ({
                color: STATUS_COLOR[l.status] === 'red' ? 'red' : l.status === 'success' ? 'green' : 'blue',
                children: `${l.status} | 起 ${l.start_time}${l.end_time ? ' 止 ' + l.end_time : ''}${l.duration != null ? ` (${l.duration}s)` : ''}${l.result ? '：' + l.result : ''}${l.error_message ? '：' + l.error_message : ''}`,
              }))} />
            ) : <Empty description="暂无日志" />,
          },
          {
            key: 'results', label: `扫描结果${findings.length ? `(${findings.length})` : ''}`,
            children: latest ? (
              <Tabs tabPosition="left" items={[
                {
                  key: 'findings', label: '发现列表',
                  children: findings.length ? (
                    <Table rowKey={(r: any) => `${r.name}-${r.port}-${r.target}`} size="small" pagination={false}
                      dataSource={findings as any} scroll={{ x: 600 }}
                      columns={[
                        { title: '风险', dataIndex: 'risk_level', key: 'risk', width: 80, render: (l: any) => <RiskTag level={l} /> },
                        { title: '名称', dataIndex: 'name', key: 'name' },
                        { title: 'CVE', dataIndex: 'cve_id', key: 'cve', render: (v: any) => v || '-' },
                        { title: '端口', dataIndex: 'port', key: 'port', width: 70 },
                        { title: '目标', dataIndex: 'target', key: 'target' },
                      ]} />
                  ) : <Empty description="未发现风险" />,
                },
                {
                  key: 'raw', label: '原始输出',
                  children: <pre style={{ maxHeight: 360, overflow: 'auto', background: 'rgba(0,0,0,0.3)', padding: 12, borderRadius: 6, color: '#9fb0c9', fontSize: 12 }}>{latest.raw_output}</pre>,
                },
              ]} />
            ) : <Empty description="暂无扫描结果" />,
          },
        ]} />
      </>
    )
  }

  return (
    <div style={glass} className="page-glass">
      <Card title="扫描任务" style={{ background: 'transparent', border: 'none' }}>
        <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
          <Col><Input allowClear placeholder="搜索任务名" prefix={<SearchOutlined />} value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} onPressEnter={() => fetchData(1)} style={{ width: 220 }} /></Col>
          <Col><Select allowClear placeholder="状态" style={{ width: 130 }} options={(Object.keys(STATUS_LABEL) as TaskStatus[]).map((s) => ({ value: s, label: STATUS_LABEL[s] }))} value={filters.status} onChange={(v) => setFilters({ ...filters, status: v })} /></Col>
          <Col><Select allowClear placeholder="引擎" style={{ width: 120 }} options={(Object.keys(ENGINE_LABEL) as TaskEngine[]).map((s) => ({ value: s, label: ENGINE_LABEL[s] }))} value={filters.engine} onChange={(v) => setFilters({ ...filters, engine: v })} /></Col>
          <Col><Button type="primary" onClick={() => fetchData(1)}>查询</Button></Col>
          <Col flex="auto" />
          <Col><Button icon={<PlusOutlined />} type="primary" onClick={openCreate}>新建任务</Button></Col>
        </Row>

        <Table rowKey="id" loading={loading} columns={columns} dataSource={data}
          pagination={{ total, current: page, pageSize: 10, showTotal: (t) => `共 ${t} 条`, onChange: (p) => { setPage(p); fetchData(p) } }}
          scroll={{ x: 1100 }} />
      </Card>

      <Drawer title={detail ? `任务详情 - ${detail.name}` : '任务详情'} width={680} open={!!detail} onClose={() => setDetail(null)} destroyOnClose>
        {detail ? renderDetail() : <Spin />}
      </Drawer>

      <Drawer title="新建任务" width={520} open={createOpen} onClose={() => setCreateOpen(false)} destroyOnClose
        extra={<Space><Button onClick={() => setCreateOpen(false)}>取消</Button><Button type="primary" onClick={onSubmit}>保存</Button></Space>}>
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="任务名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="description" label="描述"><Input.TextArea rows={2} /></Form.Item>
          <Form.Item name="engine" label="扫描引擎" rules={[{ required: true }]}><Select options={(Object.keys(ENGINE_LABEL) as TaskEngine[]).map((s) => ({ value: s, label: ENGINE_LABEL[s] }))} /></Form.Item>
          <Form.Item name="task_type" label="任务类型" rules={[{ required: true }]}><Select options={(Object.keys(TYPE_LABEL) as TaskType[]).map((s) => ({ value: s, label: TYPE_LABEL[s] }))} /></Form.Item>
          <Form.Item name="priority" label="优先级" rules={[{ required: true }]}><Select options={(Object.keys(PRIORITY_LABEL) as TaskPriority[]).map((s) => ({ value: s, label: PRIORITY_LABEL[s] }))} /></Form.Item>
          <Form.Item name="targets" label="扫描目标" extra="支持 IP / 域名 / URL，多个用换行或逗号分隔">
            <Input.TextArea rows={3} placeholder={"10.0.0.11\n10.0.0.21"} />
          </Form.Item>
          <Form.Item name="assets" label="关联资产"><Select mode="multiple" allowClear showSearch optionFilterProp="label" options={assetOptions} /></Form.Item>
          <Form.Item name="scan_ports" label="端口范围"><Input placeholder="1-1000" /></Form.Item>
          <Form.Item name="schedule_type" label="调度类型"><Select options={[{ value: 'once', label: '单次' }, { value: 'cron', label: 'Cron' }, { value: 'interval', label: '间隔' }]} /></Form.Item>
        </Form>
      </Drawer>
    </div>
  )
}
