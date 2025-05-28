import axios from 'axios'
import { ElMessage, ElLoading } from 'element-plus'

let count = 0
let loading = null

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

http.interceptors.request.use(
  config => {
    // if (count === 0) {
    //   loading = ElLoading.service()
    // }
    // count++
    const token = sessionStorage.getItem('token')
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
    // count--
    // if (count === 0) {
    //   loading.close()
    // }
    return response
  },
  error => {
    ElMessage.error(error)
    return Promise.reject(error)
  },
)

export default http
