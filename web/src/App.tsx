import { Suspense } from 'react'
import { RouterProvider } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import router from './routers'
// import './App.css'

function App() {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#1677ff',
          colorBgBase: '#0b1020',
          borderRadius: 8,
          fontSize: 13,
        },
      }}
    >
      <Suspense fallback={<div style={{ color: '#e6edf7', padding: 24 }}>Loading...</div>}>
        <RouterProvider router={router} />
      </Suspense>
    </ConfigProvider>
  )
}

export default App
