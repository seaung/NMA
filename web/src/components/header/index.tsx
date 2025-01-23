import { MenuUnfoldOutlined, MenuFoldOutlined, UserOutlined } from '@ant-design/icons'
import { Switch, Dropdown, Avatar } from 'antd'
import type { MenuProps } from 'antd'
import './index.less'

interface NavHeaderProps {
    collapsed: boolean
    onToggle: () => void
}

const NavHeader: React.FC<NavHeaderProps> = ({ collapsed, onToggle }) => {
    const items: MenuProps['items'] = [
        {
            key: 'profile',
            label: '个人信息',
            icon: <UserOutlined />
        },
        {
            type: 'divider'
        },
        {
            key: 'logout',
            label: '退出登录'
        }
    ]

    return (
        <div className='header'>
            <div className='header-left'>
                {collapsed ? (
                    <MenuUnfoldOutlined className='trigger' onClick={onToggle} />
                ) : (
                    <MenuFoldOutlined className='trigger' onClick={onToggle} />
                )}
            </div>
            <div className='header-right'>
                <Switch className='theme-switch' />
                <Dropdown menu={{ items }} placement='bottomRight'>
                    <span className='user-info'>
                        <Avatar icon={<UserOutlined />} />
                        <span className='username'>Admin</span>
                    </span>
                </Dropdown>
            </div>
        </div>
    )
}

export default NavHeader
