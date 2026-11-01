import { useEffect, useState, useRef } from 'react'
import {
  Card, Table, Button, Input, Select, Space, Drawer, Form, InputNumber,
  Switch, Tag, Popconfirm, Upload, message, Row, Col,
} from 'antd'
import { PlusOutlined, SearchOutlined, DownloadOutlined, UploadOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { getAssets, createAsset, updateAsset, deleteAsset, exportAssets, importAssets } from '@/api/assets'
import type { Asset, AssetType, AssetStatus } from '@/types'
import { RiskTag, AssetStatusTag } from '@/components/StatusTag'

const TYPE_OPTIONS = [
  { value: 'host', label: '主机' }, { value: 'web', label: 'Web应用' },
  { value: 'domain', label: '域名' }, { value: 'network', label: '网络设备' },
  { value: 'database', label: '数据库' }, { value: 'other', label: '其他' },
]
const STATUS_OPTIONS = [
  { value: 'in_use', label: '使用中' }, { value: 'idle', label: '闲置' },
  { value: 'maintenance', label: '维护中' }, { value: 'scrapped', label: '已报废' },
]

const glass: React.CSSProperties = {
  background: 'rgba(18,26,46,0.55)',
  border: '1px solid rgba(255,255,255,0.08)',
  backdropFilter: 'blur(10px)',
}

export default function AssetsPage() {
  const [data, setData] = useState<Asset[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState({ search: '', type: undefined as AssetType | undefined, status: undefined as AssetStatus | undefined, exposed: undefined as boolean | undefined })
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [editing, setEditing] = useState<Asset | null>(null)
  const [form] = Form.useForm()
  const fileRef = useRef<File | null>(null)

  const fetchData = async (p = page) => {
    setLoading(true)
    try {
      const params: any = { page: p, page_size: 10 }
      if (filters.search) params.search = filters.search
      if (filters.type) params.type = filters.type
      if (filters.status) params.status = filters.status
      if (filters.exposed !== undefined) params.exposed = String(filters.exposed)
      const res = await getAssets(params)
      setData(res.results)
      setTotal(res.count)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData(1).then(() => setPage(1)) }, [])

  const openCreate = () => { setEditing(null); form.resetFields(); form.setFieldsValue({ asset_type: 'host', asset_status: 'in_use', importance: 1, exposed: false, is_hardened: false, ports: [] }); setDrawerOpen(true) }
  const openEdit = (record: Asset) => { setEditing(record); form.setFieldsValue(record); setDrawerOpen(true) }

  const onSubmit = async () => {
    const values = await form.validateFields()
    if (editing) {
      await updateAsset(editing.id, values)
      message.success('更新成功')
    } else {
      await createAsset(values)
      message.success('创建成功')
    }
    setDrawerOpen(false)
    fetchData(page)
  }

  const onDelete = async (id: number) => { await deleteAsset(id); message.success('已删除'); fetchData(page) }

  const handleExport = async () => {
    const params: any = {}
    if (filters.search) params.search = filters.search
    if (filters.type) params.type = filters.type
    if (filters.status) params.status = filters.status
    const blob = await exportAssets(params) as unknown as Blob
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'assets.xlsx'; a.click()
    URL.revokeObjectURL(url)
  }

  const handleImport = async () => {
    if (!fileRef.current) return
    const res = await importAssets(fileRef.current) as any
    message.success(`导入完成：新增 ${res.created ?? 0}，跳过 ${res.skipped ?? 0}`)
    fileRef.current = null
    fetchData(page)
  }

  const columns: ColumnsType<Asset> = [
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: 'IP', dataIndex: 'ip', key: 'ip' },
    { title: '类型', dataIndex: 'asset_type', key: 'asset_type', render: (t) => TYPE_OPTIONS.find(o => o.value === t)?.label },
    { title: '状态', dataIndex: 'asset_status', key: 'asset_status', render: (s) => <AssetStatusTag status={s} /> },
    { title: '安全等级', dataIndex: 'security_level', key: 'security_level', render: (l) => <RiskTag level={l} /> },
    { title: '重要度', dataIndex: 'importance', key: 'importance', render: (v) => ['低', '中', '高', '核心'][v - 1] },
    { title: '暴露', dataIndex: 'exposed', key: 'exposed', render: (e) => e ? <Tag color="red">暴露</Tag> : <Tag>内网</Tag> },
    { title: '业务系统', dataIndex: 'business_system', key: 'business_system' },
    { title: '操作', key: 'action', render: (_, r) => (
      <Space>
        <Button size="small" onClick={() => openEdit(r)}>编辑</Button>
        <Popconfirm title="确认删除？" onConfirm={() => onDelete(r.id)}>
          <Button size="small" danger>删除</Button>
        </Popconfirm>
      </Space>
    ) },
  ]

  return (
    <div style={glass} className="page-glass">
      <Card title="资产管理" style={{ background: 'transparent', border: 'none' }}>
        <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
          <Col><Input allowClear placeholder="搜索名称/IP/主机名" prefix={<SearchOutlined />} value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} onPressEnter={() => fetchData(1)} style={{ width: 240 }} /></Col>
          <Col><Select allowClear placeholder="类型" options={TYPE_OPTIONS} style={{ width: 140 }} value={filters.type} onChange={(v) => setFilters({ ...filters, type: v })} /></Col>
          <Col><Select allowClear placeholder="状态" options={STATUS_OPTIONS} style={{ width: 140 }} value={filters.status} onChange={(v) => setFilters({ ...filters, status: v })} /></Col>
          <Col><Select allowClear placeholder="暴露" style={{ width: 120 }} value={filters.exposed} onChange={(v) => setFilters({ ...filters, exposed: v })} options={[{ value: true, label: '暴露' }, { value: false, label: '内网' }]} /></Col>
          <Col><Button type="primary" onClick={() => fetchData(1)}>查询</Button></Col>
          <Col flex="auto" />
          <Col><Space>
            <Button icon={<PlusOutlined />} type="primary" onClick={openCreate}>新增</Button>
            <Upload beforeUpload={(f) => { fileRef.current = f; return false }} showUploadList={false}><Button icon={<UploadOutlined />}>导入</Button></Upload>
            <Button icon={<DownloadOutlined />} onClick={handleExport}>导出</Button>
            <Button onClick={handleImport} disabled={!fileRef.current}>执行导入</Button>
          </Space></Col>
        </Row>

        <Table
          rowKey="id" loading={loading} columns={columns} dataSource={data}
          pagination={{ total, current: page, pageSize: 10, showTotal: (t) => `共 ${t} 条`, onChange: (p) => { setPage(p); fetchData(p) } }}
          scroll={{ x: 1100 }}
        />
      </Card>

      <Drawer title={editing ? '编辑资产' : '新增资产'} width={520} open={drawerOpen} onClose={() => setDrawerOpen(false)} destroyOnClose
        extra={<Space><Button onClick={() => setDrawerOpen(false)}>取消</Button><Button type="primary" onClick={onSubmit}>保存</Button></Space>}>
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="资产名称" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="ip" label="IP" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="hostname" label="主机名"><Input /></Form.Item>
          <Form.Item name="domain" label="域名"><Input /></Form.Item>
          <Form.Item name="asset_type" label="类型" rules={[{ required: true }]}><Select options={TYPE_OPTIONS} /></Form.Item>
          <Form.Item name="asset_status" label="状态" rules={[{ required: true }]}><Select options={STATUS_OPTIONS} /></Form.Item>
          <Form.Item name="security_level" label="安全等级"><Select allowClear options={[
            { value: 'critical', label: '严重' }, { value: 'high', label: '高危' }, { value: 'medium', label: '中危' }, { value: 'low', label: '低危' }, { value: 'info', label: '信息' }]} /></Form.Item>
          <Form.Item name="importance" label="重要度"><InputNumber min={1} max={4} /></Form.Item>
          <Form.Item name="exposed" label="是否暴露公网" valuePropName="checked"><Switch /></Form.Item>
          <Form.Item name="asset_group" label="资产分组"><Input /></Form.Item>
          <Form.Item name="business_system" label="业务系统"><Input /></Form.Item>
          <Form.Item name="os_type" label="操作系统类型"><Input /></Form.Item>
          <Form.Item name="description" label="描述"><Input.TextArea rows={3} /></Form.Item>
        </Form>
      </Drawer>
    </div>
  )
}
