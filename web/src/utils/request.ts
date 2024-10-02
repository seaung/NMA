import axios from 'axios'
import { message } from 'antd'

const instance = axios.create({
    baseURL: '/api',
    timeout: 80000,
    timeoutErrorMessage: '请求超时,请稍后再试!',
    withCredentials: true
})

instance.interceptors.request.use(config => {
    const token = localstorage.getItem('access_token')
    if (token) {
        config.headers.Authorization = 'Bearer ' + token
    }
    return {
        ...config
    }},
    error => {
        return Promise.reject(error)
    }
)

instance.interceptors.response.use(response => {
    const data = response.data
    if (data.code === 5000) {
        message.error(data.msg)
        localstorage.removeItem('access_token')
        location.href = '/login'
    } else if (data.code != 0) {
        message.error(data.msg)
        return Promise.reject(data)
    }
    return data.data
})


export default {
    get(url: string, params: any) {
        return axios.get(url, { params })
    },
    post(url: string, params: any) {
        return axios.post(url, params)
    }
}
