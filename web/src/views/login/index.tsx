import { useState } from 'react'
import { Form, Input, Button, Checkbox, message } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import axios from 'axios'
import './index.less'

interface LoginFormData {
  username: string
  password: string
  remember: boolean
}

const LoginPage = () => {
  const [loading, setLoading] = useState(false)

  const onFinish = async (values: LoginFormData) => {
    try {
      setLoading(true)
      const response = await axios.post('/api/login', values)
      if (response.data.success) {
        message.success('登录成功')
        // TODO: 保存token和用户信息到Redux或localStorage
        // TODO: 跳转到首页
      } else {
        message.error(response.data.message || '登录失败')
      }
    } catch (error) {
      message.error('登录请求失败，请稍后重试')
      console.error('Login error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-left" />
      <div className="login-right">
        <div className="login-form">
        <h2>系统登录</h2>
        <Form
          name="login"
          initialValues={{ remember: true }}
          onFinish={onFinish}
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Form.Item name="remember" valuePropName="checked" noStyle>
              <Checkbox>记住密码</Checkbox>
            </Form.Item>
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              block
              loading={loading}
            >
              登录
            </Button>
          </Form.Item>
        </Form>
      </div>
      </div>
    </div>
  )
}

export default LoginPage