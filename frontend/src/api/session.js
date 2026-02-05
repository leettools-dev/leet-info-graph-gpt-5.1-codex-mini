import { httpClient } from '@/utils/request'

export const createSession = async (payload) => {
  const response = await httpClient.post('/api/v1/sessions', payload)
  return response.data
}

export const listSessions = async () => {
  const response = await httpClient.get('/api/v1/sessions')
  return response.data
}

export const deleteSession = async (sessionId) => {
  const response = await httpClient.delete(`/api/v1/sessions/${sessionId}`)
  return response.data
}

export const getSession = async (sessionId) => {
  const response = await httpClient.get(`/api/v1/sessions/${sessionId}`)
  return response.data
}
