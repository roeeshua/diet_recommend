import axios from 'axios'

const api = axios.create({
    baseURL: 'http://127.0.0.1:5000/api',
    timeout: 30000
})

// 请求拦截器：自动添加 token
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// 响应拦截器：处理错误
// 响应拦截器
api.interceptors.response.use(
    response => {
        // 直接返回 response.data，这样调用方拿到的是 {code, message, data}
        return response.data
    },
    error => {
        console.error('API Error:', error)
        // 如果是网络错误或后端返回的400，返回一个标准的错误格式
        if (error.response) {
            // 后端返回了错误状态码
            return error.response.data || { code: error.response.status, message: error.message }
        }
        return { code: 500, message: error.message || '网络错误' }
    }
)

export default api