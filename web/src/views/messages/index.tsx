import { useEffect, useState } from 'react'
import {
  Card, Table, Button, Tag, Space, Popconfirm, message as Msg, Row, Col, Badge, Empty,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { getMessages, readMessage, readAllMessages, deleteMessage } from '@/api/messages'
import type { MessageItem, MessageType, MessageLevel } from '@/types'

const TYPE_LABEL: Record<MessageType, string> = {
  system: '系统', ticket: '工单', vulnerability: '漏洞', task: '任务', overdue: '逾期', other: '其他',
}
const LEVEL_COLOR: Record<MessageLevel, string> = { info: 'blue', warning: 'orange', danger: 'red' }

const glass: React.CSSProperties = {
  background: 'rgba(18,26,46,0.55)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(10px)',
}

export default function MessagesPage() {
  const [data, setData] = useState<MessageItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(1)
  const [unreadOnly, setUnreadOnly] = useState(false)

  const fetchData = async (p = page) => {
    setLoading(true)
    try {
      const params: any = { page: p, page_size: 10 }
      if (unreadOnly) params.is_read = 'false'
      const res = await getMessages(params)
      setData(res.results)
      setTotal(res.count)
    } finally { setLoading(false) }
  }

  useEffect(() => { fetchData(1).then(() => setPage(1)) }, [unreadOnly])

  const onRead = async (id: number) => {
    await readMessage(id)
    fetchData(page)
  }
  const onReadAll = async () => {
    await readAllMessages()
    Msg.success('已全部标记已读')
    fetchData(page)
  }
  const onDelete = async (id: number) => {
    await deleteMessage(id)
    fetchData(page)
  }

  const columns: ColumnsType<MessageItem> = [
    {
      title: '状态', dataIndex: 'is_read', key: 'is_read', width: 80,
      render: (v) => (v ? <Tag>已读</Tag> : <Badge status="processing" text={<Tag color="blue">未读</Tag>} />),
    },
    {
      title: '类型', dataIndex: 'message_type', key: 'message_type', width: 90,
      render: (t) => <Tag>{TYPE_LABEL[t as MessageType]}</Tag>,
    },
    {
      title: '级别', dataIndex: 'level', key: 'level', width: 90,
      render: (l) => <Tag color={LEVEL_COLOR[l as MessageLevel]}>{l === 'info' ? '普通' : l === 'warning' ? '警告' : '严重'}</Tag>,
    },
    { title: '标题', dataIndex: 'title', key: 'title' },
    { title: '内容', dataIndex: 'content', key: 'content', ellipsis: true },
    { title: '时间', dataIndex: 'message_created_at', key: 'message_created_at', width: 180 },
    {
      title: '操作', key: 'action', width: 160,
      render: (_, r) => (
        <Space>
          {!r.is_read && <Button size="small" onClick={() => onRead(r.id)}>标为已读</Button>}
          <Popconfirm title="确认删除？" onConfirm={() => onDelete(r.id)}>
            <Button size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div style={glass} className="page-glass">
      <Card title="消息中心" style={{ background: 'transparent', border: 'none' }}
        extra={<Button type="primary" onClick={onReadAll}>全部已读</Button>}>
        <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
          <Col>
            <Space>
              <Button type={!unreadOnly ? 'primary' : 'default'} onClick={() => setUnreadOnly(false)}>全部</Button>
              <Button type={unreadOnly ? 'primary' : 'default'} onClick={() => setUnreadOnly(true)}>未读</Button>
            </Space>
          </Col>
        </Row>

        {data.length === 0 && !loading ? (
          <Empty description="暂无消息" />
        ) : (
          <Table rowKey="id" loading={loading} columns={columns} dataSource={data}
            pagination={{ total, current: page, pageSize: 10, showTotal: (t) => `共 ${t} 条`, onChange: (p) => { setPage(p); fetchData(p) } }}
            scroll={{ x: 900 }} />
        )}
      </Card>
    </div>
  )
}
