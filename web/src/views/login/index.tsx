import { useEffect, useState } from 'react'
import { Form, Input, Button, Checkbox, message } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { loginThunk } from '@/store/authSlice'
import './index.less'

interface LoginFormData {
  username: string
  password: string
  remember: boolean
}

const LoginPage = () => {
  const [loading, setLoading] = useState(false)
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const token = useAppSelector((s) => s.auth.token)

  useEffect(() => {
    if (token) navigate('/dashboard', { replace: true })
  }, [token, navigate])

  const onFinish = async (values: LoginFormData) => {
    setLoading(true)
    try {
      await dispatch(loginThunk({ username: values.username, password: values.password })).unwrap()
      message.success('登录成功')
      navigate('/dashboard', { replace: true })
    } catch {
      message.error('用户名或密码错误')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-left" />
      <div className="login-right">
        <div className="login-form">
          <h2>NMA 漏洞运营系统</h2>
          <Form name="login" initialValues={{ remember: true }} onFinish={onFinish}>
            <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
              <Input prefix={<UserOutlined />} placeholder="用户名" size="large" />
            </Form.Item>

            <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
              <Input.Password prefix={<LockOutlined />} placeholder="密码" size="large" />
            </Form.Item>

            <Form.Item>
              <Form.Item name="remember" valuePropName="checked" noStyle>
                <Checkbox>记住密码</Checkbox>
              </Form.Item>
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" size="large" block loading={loading}>
                登录
              </Button>
            </Form.Item>
          </Form>
          <div className="login-tip">默认账号 admin / admin1234</div>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
