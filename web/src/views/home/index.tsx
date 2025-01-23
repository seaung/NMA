import React from 'react'
import { Card, Row, Col, List, Typography, Statistic } from 'antd'
import { SecurityScanOutlined, BugOutlined, SafetyCertificateOutlined, AlertOutlined } from '@ant-design/icons'
import { Line } from '@ant-design/charts'

const { Title } = Typography

const HomePage: React.FC = () => {
    // 模拟数据
    const statistics = [
        { title: '资产总数', value: 1234, icon: <SecurityScanOutlined />, color: '#1890ff' },
        { title: '漏洞总数', value: 56, icon: <BugOutlined />, color: '#ff4d4f' },
        { title: '已修复', value: 42, icon: <SafetyCertificateOutlined />, color: '#52c41a' },
        { title: '待处理', value: 14, icon: <AlertOutlined />, color: '#faad14' }
    ]

    const trendData = [
        { month: '1月', value: 3 },
        { month: '2月', value: 4 },
        { month: '3月', value: 6 },
        { month: '4月', value: 5 },
        { month: '5月', value: 8 },
        { month: '6月', value: 7 }
    ]

    const recentActivities = [
        '发现新漏洞: SQL注入风险 - 2小时前',
        '系统更新: 安全补丁已安装 - 4小时前',
        '资产添加: 新增Web服务器 - 6小时前',
        '漏洞修复: XSS漏洞已修复 - 1天前'
    ]

    const config = {
        data: trendData,
        xField: 'month',
        yField: 'value',
        point: {
            size: 5,
            shape: 'diamond'
        },
        label: {
            style: {
                fill: '#aaa'
            }
        }
    }

    return (
        <div style={{ padding: '24px' }}>
            <Title level={2}>系统概览</Title>
            
            <Row gutter={[16, 16]}>
                {statistics.map((stat, index) => (
                    <Col xs={24} sm={12} md={6} key={index}>
                        <Card>
                            <Statistic 
                                title={stat.title}
                                value={stat.value}
                                prefix={React.cloneElement(stat.icon, { style: { color: stat.color } })}
                                valueStyle={{ color: stat.color }}
                            />
                        </Card>
                    </Col>
                ))}
            </Row>

            <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
                <Col xs={24} lg={16}>
                    <Card title="漏洞趋势">
                        <div style={{ height: '300px' }}>
                            <Line {...config} height={280} />
                        </div>
                    </Card>
                </Col>
                <Col xs={24} lg={8}>
                    <Card title="系统动态">
                        <List
                            dataSource={recentActivities}
                            renderItem={(item) => (
                                <List.Item>
                                    {item}
                                </List.Item>
                            )}
                        />
                    </Card>
                </Col>
            </Row>
        </div>
    )
}

export default HomePage