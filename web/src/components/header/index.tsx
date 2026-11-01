import { MenuUnfoldOutlined, MenuFoldOutlined, UserOutlined, LogoutOutlined, BellOutlined } from '@ant-design/icons'
import { Dropdown, Avatar, Badge, Button } from 'antd'
import type { MenuProps } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { logoutThunk } from '@/store/authSlice'
import { getUnreadCount } from '@/api/messages'
import './index.less'

interface NavHeaderProps {
  collapsed: boolean
  onToggle: () => void
}

const NavHeader: React.FC<NavHeaderProps> = ({ collapsed, onToggle }) => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const user = useAppSelector((s) => s.auth.user)
  const token = useAppSelector((s) => s.auth.token)
  const [unread, setUnread] = useState(0)

  useEffect(() => {
    if (!token) return
    let active = true
    const load = () => getUnreadCount().then((r: any) => { if (active) setUnread(r.count) }).catch(() => {})
    load()
    const t = setInterval(load, 30000)
    return () => { active = false; clearInterval(t) }
  }, [token])

  const items: MenuProps['items'] = [
    {
      key: 'profile',
      label: '个人信息',
      icon: <UserOutlined />,
    },
    { type: 'divider' },
    {
      key: 'logout',
      label: '退出登录',
      icon: <LogoutOutlined />,
    },
  ]

  const onClick: MenuProps['onClick'] = ({ key }) => {
    if (key === 'logout') {
      dispatch(logoutThunk())
      navigate('/login', { replace: true })
    }
  }

  return (
    <div className="header">
      <div className="header-left">
        {collapsed ? (
          <MenuUnfoldOutlined className="trigger" onClick={onToggle} />
        ) : (
          <MenuFoldOutlined className="trigger" onClick={onToggle} />
        )}
      </div>
      <div className="header-right">
        <Badge count={unread} size="small" offset={[-2, 2]}>
          <Button type="text" icon={<BellOutlined style={{ fontSize: 18, color: '#e6edf7' }} />} onClick={() => navigate('/messages')} />
        </Badge>
        <Dropdown menu={{ items, onClick }} placement="bottomRight">
          <span className="user-info">
            <Avatar icon={<UserOutlined />} />
            <span className="username">{user?.nickname || user?.username || '未登录'}</span>
          </span>
        </Dropdown>
      </div>
    </div>
  )
}

export default NavHeader
