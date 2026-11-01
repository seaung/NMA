import request from '@/utils/request'
import type { Paginated } from '@/types'

export interface UserBrief {
  id: number
  username: string
  nickname: string
  email: string
  is_superuser: boolean
  dept: { id: number; name: string } | null
  roles: string[]
}

export const getUsers = (params?: any): Promise<Paginated<UserBrief>> =>
  request.get('/api/v1/users/', params)
