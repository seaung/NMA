import React from 'react'
import { Layout } from 'antd'
import NavHeader from '@/components/header'
import NavFooter from '@/components/footer'

const { Content, Sider } = Layout


const App: React.FC = () => {
    return (
        <>
            <Layout>
                <Sider></Sider>
                <Layout>
                    <NavHeader/>
                    <div className='content'>
                        <div className='wrapper'>
                            <Outlet></Outlet>
                        </div>
                        <NavFooter/>
                    </div>
                </Layout>
            </Layout>
        </>
    )
}

export default App
