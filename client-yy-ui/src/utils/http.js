import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

http.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.token = token
    }
    return config
  },
  error => {
    ElMessage.error(error)
    return Promise.reject(error)
  },
)

http.interceptors.response.use(
  response => {
    return response
  },
  error => {
    ElMessage.error(error)
    return Promise.reject(error)
  },
)

export default http
