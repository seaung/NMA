import request from '@/utils/request'

export interface LoginPayload {
  username: string
  password: string
}

export const login = (data: LoginPayload) => request.post('/api/v1/auth/login/', data)
export const refreshToken = (refresh: string) =>
  request.post('/api/v1/auth/refresh/', { refresh })
export const logout = (refresh: string) =>
  request.post('/api/v1/auth/logout/', { refresh })
export const getMe = () => request.get('/api/v1/auth/me/')
export const changePassword = (data: { old_password: string; new_password: string }) =>
  request.put('/api/v1/auth/password/', data)
