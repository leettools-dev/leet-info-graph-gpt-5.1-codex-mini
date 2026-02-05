import axios from 'axios'

const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export const httpClient = axios.create({
  baseURL: apiBase,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * Configure the Authorization header for subsequent requests.
 */
export const setAuthToken = (token) => {
  if (token) {
    httpClient.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    delete httpClient.defaults.headers.common.Authorization
  }
}

