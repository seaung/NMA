import request from '@/utils/request'
import type { Task, Paginated } from '@/types'

export const getTasks = (params?: any): Promise<Paginated<Task>> =>
  request.get('/api/v1/tasks/', params)

export const getTask = (id: number): Promise<Task> =>
  request.get(`/api/v1/tasks/${id}/`)

export const createTask = (data: Partial<Task>) =>
  request.post('/api/v1/tasks/', data)

export const updateTask = (id: number, data: Partial<Task>) =>
  request.put(`/api/v1/tasks/${id}/`, data)

export const deleteTask = (id: number) =>
  request.delete(`/api/v1/tasks/${id}/`)

export const runTask = (id: number) =>
  request.post(`/api/v1/tasks/${id}/run/`)

export const cancelTask = (id: number) =>
  request.post(`/api/v1/tasks/${id}/cancel/`)
