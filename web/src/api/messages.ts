import request from '@/utils/request'
import type { MessageItem, Paginated } from '@/types'

export const getMessages = (params?: any): Promise<Paginated<MessageItem>> =>
  request.get('/api/v1/messages/', params)

export const readMessage = (id: number) =>
  request.post(`/api/v1/messages/${id}/read/`)

export const readAllMessages = () =>
  request.post(`/api/v1/messages/read_all/`)

export const deleteMessage = (id: number) =>
  request.delete(`/api/v1/messages/${id}/`)

export const getUnreadCount = () =>
  request.get('/api/v1/messages/unread_count/')
