import {MenuUnfoldOutlined, MenuFoldOutlined} from '@ant-design/icons'
import {Breadcrumb, Switch, Dropdown} from 'antd'
import type {MenuProps} from 'antd'


const NavHeader = () => {
    const items: MenuProps['items'] = [
        {
            key: 'username',
            label: '用户名:'
        },
        {
            key: 'email',
            label: '邮箱地址:'
        },
        {
            key: 'logout',
            label: '退出'
        }
    ]

    return (
        <div className='headers'>
            <div className='left'></div>
            <div className='rigth'>
                <Switch />
                <Dropdown menu={{ items, onClick }} tigger={['click']}>
                    <span className={}>username</span>
                </Dropdown>
            </div>
        </div>
    )
}

export default NavHeader
