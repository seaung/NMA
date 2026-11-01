import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosResponse } from 'axios'
import { message } from 'antd'

declare module 'axios' {
  export interface AxiosRequestConfig {
    _retry?: boolean
  }
}

const TOKEN_KEY = 'nma_auth'

export interface AuthTokens {
  access: string
  refresh: string
}

export function getTokens(): AuthTokens | null {
  const raw = localStorage.getItem(TOKEN_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as AuthTokens
  } catch {
    return null
  }
}

export function setTokens(t: AuthTokens): void {
  localStorage.setItem(TOKEN_KEY, JSON.stringify(t))
}

export function clearTokens(): void {
  localStorage.removeItem(TOKEN_KEY)
}

const instance: AxiosInstance = axios.create({
  baseURL: '',
  timeout: 80000,
})

// 请求拦截：附加 Bearer Token
instance.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const t = getTokens()
  if (t?.access) {
    config.headers.Authorization = `Bearer ${t.access}`
  }
  return config
})

// 401 刷新重放
let isRefreshing = false
let pendingQueue: Array<(token: string) => void> = []

instance.interceptors.response.use(
  (response: AxiosResponse) => {
    const body = response.data
    // 统一响应信封 {code, msg, data}
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code === 0) return body.data
      message.error(body.msg || '请求失败')
      return Promise.reject(body)
    }
    return body
  },
  async (error) => {
    const status = error.response?.status
    const original = error.config

    if (status === 401 && original && !original._retry) {
      const t = getTokens()
      if (t?.refresh && !isRefreshing) {
        isRefreshing = true
        try {
          const res = await axios.post('/api/v1/auth/refresh/', { refresh: t.refresh })
          const body = res.data?.data ?? res.data
          const newAccess = body?.access
          const newRefresh = body?.refresh ?? t.refresh
          setTokens({ access: newAccess, refresh: newRefresh })
          isRefreshing = false
          pendingQueue.forEach((cb) => cb(newAccess))
          pendingQueue = []
          original._retry = true
          original.headers.Authorization = `Bearer ${newAccess}`
          return instance(original)
        } catch (e) {
          isRefreshing = false
          pendingQueue = []
          clearTokens()
          message.error('登录已过期，请重新登录')
          location.href = '/login'
          return Promise.reject(e)
        }
      }
      // 已有刷新在进行，排队等待
      return new Promise((resolve) => {
        pendingQueue.push((token: string) => {
          original.headers.Authorization = `Bearer ${token}`
          resolve(instance(original))
        })
      })
    }

    const body = error.response?.data
    const msg = body?.msg || error.message || '请求失败'
    if (status !== 401) message.error(msg)
    return Promise.reject(error)
  }
)

const request = {
  get: (url: string, params?: any) => instance.get(url, { params }) as Promise<any>,
  post: (url: string, data?: any) => instance.post(url, data) as Promise<any>,
  put: (url: string, data?: any) => instance.put(url, data) as Promise<any>,
  patch: (url: string, data?: any) => instance.patch(url, data) as Promise<any>,
  delete: (url: string, params?: any) => instance.delete(url, { params }) as Promise<any>,
  instance,
}

export default request
