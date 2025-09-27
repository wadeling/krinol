import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const isLoading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userInfo = computed(() => user.value)

  // 方法
  const setUser = (userData) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const setToken = (tokenValue) => {
    token.value = tokenValue
    localStorage.setItem('token', tokenValue)
    
    // 设置API默认请求头
    if (tokenValue) {
      api.defaults.headers.common['Authorization'] = `Bearer ${tokenValue}`
    } else {
      delete api.defaults.headers.common['Authorization']
    }
  }

  const clearUser = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    delete api.defaults.headers.common['Authorization']
  }

  const login = async (credentials) => {
    isLoading.value = true
    try {
      const formData = new FormData()
      formData.append('username', credentials.username)
      formData.append('password', credentials.password)
      
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
      
      setUser(response.data.user)
      setToken(response.data.access_token)
      
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || '登录失败' 
      }
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    clearUser()
  }

  const register = async (userData) => {
    isLoading.value = true
    try {
      const response = await api.post('/auth/register', userData)
      
      setUser(response.data.user)
      setToken(response.data.access_token)
      
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || '注册失败' 
      }
    } finally {
      isLoading.value = false
    }
  }

  const validateInviteCode = async (inviteCode) => {
    try {
      const response = await api.post('/auth/validate-invite', {
        invite_code: inviteCode
      })
      return response.data
    } catch (error) {
      return {
        is_valid: false,
        message: '邀请码验证失败'
      }
    }
  }

  const getCurrentUser = async () => {
    if (!token.value) return null
    
    try {
      const response = await api.get('/auth/me')
      setUser(response.data)
      return response.data
    } catch (error) {
      // Token可能已过期，清除用户信息
      clearUser()
      return null
    }
  }

  // 初始化时从localStorage恢复用户信息
  const initUser = () => {
    const savedUser = localStorage.getItem('user')
    if (savedUser && token.value) {
      user.value = JSON.parse(savedUser)
      // 设置API默认请求头
      api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    }
  }

  return {
    // 状态
    user,
    token,
    isLoading,
    
    // 计算属性
    isAuthenticated,
    userInfo,
    
    // 方法
    setUser,
    setToken,
    clearUser,
    login,
    logout,
    register,
    validateInviteCode,
    getCurrentUser,
    initUser
  }
})