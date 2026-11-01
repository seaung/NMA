import React, { useEffect, useMemo, useState } from 'react'
import { Layout as AntLayout, Menu, Spin } from 'antd'
import { useNavigate, useLocation, Outlet } from 'react-router-dom'
import * as Icons from '@ant-design/icons'
import NavHeader from '@/components/header'
import NavFooter from '@/components/footer'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { loadProfile, type MenuNode } from '@/store/authSlice'
import './index.less'

const { Content, Sider } = AntLayout

function renderIcon(name?: string) {
  const Cmp = (Icons as unknown as Record<string, React.ComponentType>)[name || '']
  return Cmp ? <Cmp /> : <Icons.AppstoreOutlined />
}

function buildMenuItems(nodes: MenuNode[]): any[] {
  return nodes
    .filter((n) => n.visible !== false && n.menu_type === 'menu')
    .map((n) => ({
      key: n.path || String(n.id),
      icon: renderIcon(n.icon),
      label: n.name,
      children: n.children && n.children.length ? buildMenuItems(n.children) : undefined,
    }))
}

const Layout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false)
  const token = useAppSelector((s) => s.auth.token)
  const loaded = useAppSelector((s) => s.auth.loaded)
  const menus = useAppSelector((s) => s.auth.menus)
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    if (!token) {
      navigate('/login', { replace: true })
    }
  }, [token, navigate])

  useEffect(() => {
    if (token && !loaded) {
      dispatch(loadProfile())
    }
  }, [token, loaded, dispatch])

  const items = useMemo(() => buildMenuItems(menus), [menus])
  const selectedKey = location.pathname

  if (!token) return null
  if (!loaded) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div className="logo" />
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={items}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <AntLayout>
        <NavHeader collapsed={collapsed} onToggle={() => setCollapsed((v) => !v)} />
        <Content
          className="site-content"
          style={{ overflow: 'auto', height: 'calc(100vh - 64px - 70px)', padding: 24 }}
        >
          <Outlet />
        </Content>
        <NavFooter />
      </AntLayout>
    </AntLayout>
  )
}

export default Layout
