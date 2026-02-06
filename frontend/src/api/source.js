import { httpClient } from '@/utils/request'

export const listSources = async (sessionId) => {
  const response = await httpClient.get(`/api/v1/sessions/${sessionId}/sources`)
  return response.data
}
