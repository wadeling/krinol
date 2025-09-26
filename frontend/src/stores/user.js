import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // 动作
  const login = async (credentials) => {
    try {
      loading.value = true
      const response = await api.post('/auth/login', {
        username: credentials.email,
        password: credentials.password
      })
      
      token.value = response.data.access_token
      localStorage.setItem('token', token.value)
      
      // 获取用户信息
      await fetchUserInfo()
      
      ElMessage.success('登录成功')
      return true
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '登录失败')
      return false
    } finally {
      loading.value = false
    }
  }

  const register = async (userData) => {
    try {
      loading.value = true
      await api.post('/auth/register', userData)
      ElMessage.success('注册成功，请登录')
      return true
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '注册失败')
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    ElMessage.success('已退出登录')
  }

  const fetchUserInfo = async () => {
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
    } catch (error) {
      console.error('获取用户信息失败:', error)
      logout()
    }
  }

  const initAuth = async () => {
    if (token.value) {
      await fetchUserInfo()
    }
  }

  const updateProfile = async (userData) => {
    try {
      loading.value = true
      const response = await api.put('/auth/me', userData)
      user.value = response.data
      ElMessage.success('个人信息更新成功')
      return true
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '更新失败')
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    fetchUserInfo,
    initAuth,
    updateProfile
  }
})
