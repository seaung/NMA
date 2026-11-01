import { useEffect, useState, useRef } from 'react'
import {
  Card, Table, Button, Input, Select, Space, Drawer, Form, Timeline,
  Tag, Popconfirm, Upload, message, Row, Col, Descriptions, InputNumber,
} from 'antd'
import { PlusOutlined, SearchOutlined, DownloadOutlined, UploadOutlined, SwapOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import {
  getVulnerabilities, createVulnerability, deleteVulnerability,
  transitionVulnerability, exportVulnerabilities, importVulnerabilities,
} from '@/api/vulnerabilities'
import { getAssets } from '@/api/assets'
import type { Vulnerability, VulnStatus, RiskLevel, VulnSource, Asset } from '@/types'
import { RiskTag, VulnStatusTag, VULN_STATUS_LABEL, RISK_LABEL } from '@/components/StatusTag'

const RISK_OPTIONS = (['critical', 'high', 'medium', 'low', 'info'] as RiskLevel[]).map((v) => ({ value: v, label: RISK_LABEL[v] }))
const STATUS_OPTIONS = (Object.keys(VULN_STATUS_LABEL) as VulnStatus[]).map((v) => ({ value: v, label: VULN_STATUS_LABEL[v] }))
const SOURCE_OPTIONS = [
  { value: 'manual', label: '手工录入' }, { value: 'scan', label: '扫描发现' },
  { value: 'import', label: '批量导入' }, { value: 'intel', label: '威胁情报' },
]
const TRANSITIONS: Record<VulnStatus, VulnStatus[]> = {
  unverified: ['verified', 'false_positive', 'risk_accepted', 'closed'],
  verified: ['fixing', 'false_positive', 'risk_accepted', 'closed'],
  fixing: ['pending_retest', 'risk_accepted', 'closed'],
  pending_retest: ['fixed', 'fixing', 'risk_accepted', 'closed'],
  fixed: ['closed', 'pending_retest', 'risk_accepted'],
  closed: ['unverified'],
  false_positive: ['unverified'],
  risk_accepted: ['unverified', 'closed'],
}

const glass: React.CSSProperties = {
  background: 'rgba(18,26,46,0.55)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(10px)',
}

export default function VulnerabilitiesPage() {
  const [data, setData] = useState<Vulnerability[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState({ search: '', risk_level: undefined as RiskLevel | undefined, status: undefined as VulnStatus | undefined, source: undefined as VulnSource | undefined })
  const [detail, setDetail] = useState<Vulnerability | null>(null)
  const [createOpen, setCreateOpen] = useState(false)
  const [form] = Form.useForm()
  const [assetOptions, setAssetOptions] = useState<{ value: number; label: string }[]>([])
  const [txOpen, setTxOpen] = useState(false)
  const [txTarget, setTxTarget] = useState<VulnStatus | undefined>()
  const [txNote, setTxNote] = useState('')
  const [txLoading, setTxLoading] = useState(false)
  const fileRef = useRef<File | null>(null)

  const fetchData = async (p = page) => {
    setLoading(true)
    try {
      const params: any = { page: p, page_size: 10 }
      if (filters.search) params.search = filters.search
      if (filters.risk_level) params.risk_level = filters.risk_level
      if (filters.status) params.status = filters.status
      if (filters.source) params.source = filters.source
      const res = await getVulnerabilities(params)
      setData(res.results)
      setTotal(res.count)
    } finally { setLoading(false) }
  }

  useEffect(() => { fetchData(1).then(() => setPage(1)) }, [])

  const openCreate = async () => {
    const res = await getAssets({ page: 1, page_size: 100 })
    setAssetOptions(res.results.map((a: Asset) => ({ value: a.id, label: `${a.name}(${a.ip})` })))
    form.resetFields(); form.setFieldsValue({ risk_level: 'medium', status: 'unverified', source: 'manual', asset_ids: [] })
    setCreateOpen(true)
  }

  const onSubmit = async () => {
    const values = await form.validateFields()
    await createVulnerability(values)
    message.success('创建成功')
    setCreateOpen(false)
    fetchData(page)
  }

  const onDelete = async (id: number) => { await deleteVulnerability(id); message.success('已删除'); fetchData(page) }

  const openTx = (record: Vulnerability) => { setDetail(record); setTxTarget(undefined); setTxNote(''); setTxOpen(true) }
  const doTransition = async () => {
    if (!detail || !txTarget) return
    setTxLoading(true)
    try {
      await transitionVulnerability(detail.id, txTarget, txNote)
      message.success('状态已更新')
      setTxOpen(false)
      const fresh = await getVulnerabilities({ page, page_size: 10 })
      setData(fresh.results); setTotal(fresh.count)
      const updated = await import('@/api/vulnerabilities').then((m) => m.getVulnerability(detail.id))
      setDetail(updated)
    } finally { setTxLoading(false) }
  }

  const handleExport = async () => {
    const params: any = {}
    if (filters.search) params.search = filters.search
    if (filters.risk_level) params.risk_level = filters.risk_level
    if (filters.status) params.status = filters.status
    if (filters.source) params.source = filters.source
    const blob = await exportVulnerabilities(params) as unknown as Blob
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'vulnerabilities.xlsx'; a.click()
    URL.revokeObjectURL(url)
  }

  const handleImport = async () => {
    if (!fileRef.current) return
    const res = await importVulnerabilities(fileRef.current) as any
    message.success(`导入完成：新增 ${res.created ?? 0}，跳过 ${res.skipped ?? 0}`)
    fileRef.current = null
    fetchData(page)
  }

  const columns: ColumnsType<Vulnerability> = [
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: 'CVE', dataIndex: 'cve_id', key: 'cve_id', render: (v) => v || '-' },
    { title: '风险', dataIndex: 'risk_level', key: 'risk_level', render: (l) => <RiskTag level={l} /> },
    { title: 'CVSS', dataIndex: 'cvss_score', key: 'cvss_score', render: (v) => v ?? '-' },
    { title: '状态', dataIndex: 'status', key: 'status', render: (s) => <VulnStatusTag status={s} /> },
    { title: '评分', dataIndex: 'risk_score', key: 'risk_score' },
    { title: '来源', dataIndex: 'source', key: 'source' },
    { title: '影响资产', key: 'assets', render: (_, r) => r.assets.map((a) => <Tag key={a.id}>{a.asset_ip || a.asset_name}</Tag>) },
    { title: '发现时间', dataIndex: 'discovered_at', key: 'discovered_at' },
    { title: '操作', key: 'action', render: (_, r) => (
      <Space>
        <Button size="small" onClick={() => openTx(r)}>详情/流转</Button>
        <Popconfirm title="确认删除？" onConfirm={() => onDelete(r.id)}>
          <Button size="small" danger>删除</Button>
        </Popconfirm>
      </Space>
    ) },
  ]

  return (
    <div style={glass} className="page-glass">
      <Card title="漏洞管理" style={{ background: 'transparent', border: 'none' }}>
        <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
          <Col><Input allowClear placeholder="搜索名称/CVE" prefix={<SearchOutlined />} value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} onPressEnter={() => fetchData(1)} style={{ width: 240 }} /></Col>
          <Col><Select allowClear placeholder="风险等级" options={RISK_OPTIONS} style={{ width: 130 }} value={filters.risk_level} onChange={(v) => setFilters({ ...filters, risk_level: v })} /></Col>
          <Col><Select allowClear placeholder="状态" options={STATUS_OPTIONS} style={{ width: 140 }} value={filters.status} onChange={(v) => setFilters({ ...filters, status: v })} /></Col>
          <Col><Select allowClear placeholder="来源" options={SOURCE_OPTIONS} style={{ width: 140 }} value={filters.source} onChange={(v) => setFilters({ ...filters, source: v })} /></Col>
          <Col><Button type="primary" onClick={() => fetchData(1)}>查询</Button></Col>
          <Col flex="auto" />
          <Col><Space>
            <Button icon={<PlusOutlined />} type="primary" onClick={openCreate}>新增</Button>
            <Upload beforeUpload={(f) => { fileRef.current = f; return false }} showUploadList={false}><Button icon={<UploadOutlined />}>导入</Button></Upload>
            <Button icon={<DownloadOutlined />} onClick={handleExport}>导出</Button>
            <Button onClick={handleImport} disabled={!fileRef.current}>执行导入</Button>
          </Space></Col>
        </Row>

        <Table rowKey="id" loading={loading} columns={columns} dataSource={data}
          pagination={{ total, current: page, pageSize: 10, showTotal: (t) => `共 ${t} 条`, onChange: (p) => { setPage(p); fetchData(p) } }}
          scroll={{ x: 1200 }} />
      </Card>

      <Drawer title="漏洞详情 / 状态流转" width={560} open={txOpen} onClose={() => setTxOpen(false)} destroyOnClose>
        {detail && (
          <>
            <Descriptions column={1} size="small" bordered>
              <Descriptions.Item label="名称">{detail.name}</Descriptions.Item>
              <Descriptions.Item label="CVE">{detail.cve_id || '-'}</Descriptions.Item>
              <Descriptions.Item label="风险等级"><RiskTag level={detail.risk_level} /></Descriptions.Item>
              <Descriptions.Item label="CVSS">{detail.cvss_score ?? '-'}</Descriptions.Item>
              <Descriptions.Item label="当前状态"><VulnStatusTag status={detail.status} /></Descriptions.Item>
              <Descriptions.Item label="风险评分">{detail.risk_score}</Descriptions.Item>
              <Descriptions.Item label="影响范围">{detail.impact || '-'}</Descriptions.Item>
              <Descriptions.Item label="修复建议">{detail.solution || '-'}</Descriptions.Item>
            </Descriptions>
            <div style={{ margin: '16px 0' }}>
              <Space>
                <span>状态流转：</span>
                <Select style={{ width: 160 }} placeholder="选择目标状态" value={txTarget} onChange={setTxTarget}
                  options={TRANSITIONS[detail.status].map((s) => ({ value: s, label: VULN_STATUS_LABEL[s] }))} />
                <Button type="primary" icon={<SwapOutlined />} loading={txLoading} disabled={!txTarget} onClick={doTransition}>提交</Button>
              </Space>
              <Input placeholder="流转备注（可选）" value={txNote} onChange={(e) => setTxNote(e.target.value)} style={{ marginTop: 8 }} />
            </div>
            <Timeline items={detail.histories.map((h) => ({
              color: 'blue',
              children: `${h.operator_name || '系统'} 将状态从 ${h.old_status ? VULN_STATUS_LABEL[h.old_status] : '-'} 变更为 ${h.new_status ? VULN_STATUS_LABEL[h.new_status] : '-'}（${h.created_at}）${h.note ? '：' + h.note : ''}`,
            }))} />
          </>
        )}
      </Drawer>

      <Drawer title="新增漏洞" width={520} open={createOpen} onClose={() => setCreateOpen(false)} destroyOnClose
        extra={<Space><Button onClick={() => setCreateOpen(false)}>取消</Button><Button type="primary" onClick={onSubmit}>保存</Button></Space>}>
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="漏洞名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="cve_id" label="CVE编号"><Input /></Form.Item>
          <Form.Item name="risk_level" label="风险等级" rules={[{ required: true }]}><Select options={RISK_OPTIONS} /></Form.Item>
          <Form.Item name="cvss_score" label="CVSS评分"><InputNumber min={0} max={10} step={0.1} style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="status" label="状态" rules={[{ required: true }]}><Select options={STATUS_OPTIONS} /></Form.Item>
          <Form.Item name="source" label="来源" rules={[{ required: true }]}><Select options={SOURCE_OPTIONS} /></Form.Item>
          <Form.Item name="asset_ids" label="关联资产"><Select mode="multiple" options={assetOptions} placeholder="选择受影响资产" /></Form.Item>
          <Form.Item name="description" label="描述"><Input.TextArea rows={3} /></Form.Item>
          <Form.Item name="impact" label="影响范围"><Input.TextArea rows={2} /></Form.Item>
          <Form.Item name="solution" label="修复建议"><Input.TextArea rows={2} /></Form.Item>
        </Form>
      </Drawer>
    </div>
  )
}
