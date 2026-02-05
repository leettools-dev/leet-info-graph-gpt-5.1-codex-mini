import axios from 'axios'

const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const client = axios.create({ baseURL: apiBase })

export const checkHealth = () => client.get('/api/v1/health')
