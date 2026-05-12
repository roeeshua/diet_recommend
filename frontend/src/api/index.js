import axios from 'axios'

const api = axios.create({
    baseURL: 'http://127.0.0.1:5000/api',
    timeout: 3000000
})

// 请求拦截器：自动添加 token
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

api.interceptors.response.use(
    response => response.data,
    error => {
        // 用户主动取消的请求，继续抛出让调用方处理
        if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
            return Promise.reject(error)
        }
        console.error('API Error:', error)
        if (error.response) {
            return error.response.data || { code: error.response.status, message: error.message }
        }
        return { code: 500, message: error.message || '网络错误' }
    }
)

export default api