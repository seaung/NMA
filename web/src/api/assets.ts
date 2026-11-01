import request from '@/utils/request'
import type { Asset, Paginated } from '@/types'

export const getAssets = (params?: any): Promise<Paginated<Asset>> =>
  request.get('/api/v1/assets/', params)

export const getAsset = (id: number): Promise<Asset> =>
  request.get(`/api/v1/assets/${id}/`)

export const createAsset = (data: Partial<Asset>) =>
  request.post('/api/v1/assets/', data)

export const updateAsset = (id: number, data: Partial<Asset>) =>
  request.put(`/api/v1/assets/${id}/`, data)

export const deleteAsset = (id: number) =>
  request.delete(`/api/v1/assets/${id}/`)

export const exportAssets = (params?: any) =>
  request.instance.get('/api/v1/assets/export_excel/', {
    params,
    responseType: 'blob',
  })

export const importAssets = (file: File) => {
  const fd = new FormData()
  fd.append('file', file)
  return request.instance.post('/api/v1/assets/import_excel/', fd)
}
