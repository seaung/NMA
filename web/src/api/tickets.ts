import request from '@/utils/request'
import type { Ticket, Paginated } from '@/types'

export const getTickets = (params?: any): Promise<Paginated<Ticket>> =>
  request.get('/api/v1/tickets/', params)

export const getTicket = (id: number): Promise<Ticket> =>
  request.get(`/api/v1/tickets/${id}/`)

export const createTicket = (data: Partial<Ticket>) =>
  request.post('/api/v1/tickets/', data)

export const updateTicket = (id: number, data: Partial<Ticket>) =>
  request.put(`/api/v1/tickets/${id}/`, data)

export const deleteTicket = (id: number) =>
  request.delete(`/api/v1/tickets/${id}/`)

export const assignTicket = (id: number, assignee_id: number) =>
  request.post(`/api/v1/tickets/${id}/assign/`, { assignee_id })

export const transitionTicket = (id: number, status: string, note = '', resolution = '') =>
  request.post(`/api/v1/tickets/${id}/change_status/`, { status, note, resolution })

export const addComment = (id: number, content: string) =>
  request.post(`/api/v1/tickets/${id}/add_comment/`, { content })
