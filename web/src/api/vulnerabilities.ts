import request from '@/utils/request'
import type { Vulnerability, Paginated } from '@/types'

export const getVulnerabilities = (params?: any): Promise<Paginated<Vulnerability>> =>
  request.get('/api/v1/vulnerabilities/', params)

export const getVulnerability = (id: number): Promise<Vulnerability> =>
  request.get(`/api/v1/vulnerabilities/${id}/`)

export const createVulnerability = (data: Partial<Vulnerability>) =>
  request.post('/api/v1/vulnerabilities/', data)

export const updateVulnerability = (id: number, data: Partial<Vulnerability>) =>
  request.put(`/api/v1/vulnerabilities/${id}/`, data)

export const deleteVulnerability = (id: number) =>
  request.delete(`/api/v1/vulnerabilities/${id}/`)

export const transitionVulnerability = (id: number, status: string, note = '') =>
  request.post(`/api/v1/vulnerabilities/${id}/transition/`, { status, note })

export const exportVulnerabilities = (params?: any) =>
  request.instance.get('/api/v1/vulnerabilities/export_excel/', {
    params,
    responseType: 'blob',
  })

export const importVulnerabilities = (file: File) => {
  const fd = new FormData()
  fd.append('file', file)
  return request.instance.post('/api/v1/vulnerabilities/import_excel/', fd)
}
