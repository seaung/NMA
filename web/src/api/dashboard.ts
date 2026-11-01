import request from '@/utils/request'
import type { DashboardData } from '@/types'

export const getDashboard = (): Promise<DashboardData> =>
  request.get('/api/v1/dashboard/')
