import React, { useState } from 'react'
import { Layout, Menu } from 'antd'
import { Outlet } from 'react-router-dom'
import {
    UserOutlined,
    VideoCameraOutlined,
    UploadOutlined,
} from '@ant-design/icons'
import NavHeader from '@/components/header'
import NavFooter from '@/components/footer'
import './index.less'

const { Content, Sider } = Layout

const App: React.FC = () => {
    const [collapsed, setCollapsed] = useState(false)

    const items = [
        {
            key: '1',
            icon: <UserOutlined />,
            label: '用户管理',
        },
        {
            key: '2',
            icon: <VideoCameraOutlined />,
            label: '系统监控',
        },
        {
            key: '3',
            icon: <UploadOutlined />,
            label: '数据上传',
        },
    ]

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Sider trigger={null} collapsible collapsed={collapsed}>
                <div className="logo" />
                <Menu
                    theme="dark"
                    mode="inline"
                    defaultSelectedKeys={['1']}
                    items={items}
                />
            </Sider>
            <Layout>
                <NavHeader collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
                <Content className="site-content" style={{ overflow: 'auto', height: 'calc(100vh - 64px - 70px)' }}>
                    <div className="content-wrapper">
                        <Outlet />
                    </div>
                </Content>
                <NavFooter />
            </Layout>
        </Layout>
    )
}

export default App
