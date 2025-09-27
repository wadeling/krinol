<template>
  <div class="login-container">
    <!-- 左上角 Logo -->
    <div class="logo-section">
      <div class="logo">
        <div class="logo-icon">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="8" fill="url(#gradient)"/>
            <path d="M8 12h16v2H8v-2zm0 4h16v2H8v-2zm0 4h12v2H8v-2z" fill="white"/>
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#6366f1"/>
                <stop offset="100%" style="stop-color:#8b5cf6"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <span class="logo-text">Krinol</span>
      </div>
    </div>

    <!-- 登录表单容器 -->
    <div class="login-form-container">
      <div class="login-form-wrapper">
        <!-- 登录/注册切换 -->
        <div class="form-tabs">
          <button
            @click="isLogin = true"
            :class="['tab-button', { active: isLogin }]"
          >
            登录
          </button>
          <button
            @click="isLogin = false"
            :class="['tab-button', { active: !isLogin }]"
          >
            注册
          </button>
        </div>

        <!-- 登录表单 -->
        <div v-if="isLogin" class="login-form">
          <h1 class="form-title">登录</h1>
          <p class="form-subtitle">Hi, 欢迎回来 👋</p>


          <form @submit.prevent="handleLogin" class="form">
            <div class="form-group">
              <label for="username" class="form-label">用户名</label>
              <input
                id="username"
                v-model="loginForm.username"
                type="text"
                required
                class="form-input"
                placeholder="请输入用户名"
              />
            </div>

            <div class="form-group">
              <label for="password" class="form-label">密码</label>
              <div class="password-input-wrapper">
                <input
                  id="password"
                  v-model="loginForm.password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  class="form-input"
                  placeholder="请输入密码"
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="showPassword = !showPassword"
                >
                  <svg v-if="!showPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                </button>
              </div>
            </div>

            <div class="form-options">
              <label class="checkbox-wrapper">
                <input type="checkbox" v-model="rememberMe" class="checkbox">
                <span class="checkbox-label">记住我</span>
              </label>
              <a href="#" class="forgot-password">忘记密码？</a>
            </div>

            <button
              type="submit"
              :disabled="isLoading"
              class="login-btn"
            >
              {{ isLoading ? '登录中...' : '登录' }}
            </button>
          </form>

          <div class="register-link">
            <span>还没有账号？</span>
            <a href="#" @click.prevent="isLogin = false" class="register-link-text">创建账号</a>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M7 17L17 7M17 7H7M17 7V17"/>
            </svg>
          </div>
        </div>

        <!-- 注册表单 -->
        <div v-else class="register-form">
          <h1 class="form-title">注册</h1>
          <p class="form-subtitle">创建您的 Krinol 账号</p>

          <form @submit.prevent="handleRegister" class="form">
            <div class="form-group">
              <label for="inviteCode" class="form-label">邀请码</label>
              <input
                id="inviteCode"
                v-model="registerForm.inviteCode"
                type="text"
                required
                class="form-input"
                placeholder="请输入邀请码"
                @blur="validateInviteCode"
              />
              <p v-if="inviteCodeStatus" class="form-message" :class="inviteCodeStatus.isValid ? 'success' : 'error'">
                {{ inviteCodeStatus.message }}
              </p>
            </div>

            <div class="form-group">
              <label for="regUsername" class="form-label">用户名</label>
              <input
                id="regUsername"
                v-model="registerForm.username"
                type="text"
                required
                class="form-input"
                placeholder="请输入用户名"
              />
            </div>

            <div class="form-group">
              <label for="email" class="form-label">邮箱</label>
              <input
                id="email"
                v-model="registerForm.email"
                type="email"
                required
                class="form-input"
                placeholder="请输入邮箱地址"
              />
            </div>

            <div class="form-group">
              <label for="fullName" class="form-label">姓名（可选）</label>
              <input
                id="fullName"
                v-model="registerForm.fullName"
                type="text"
                class="form-input"
                placeholder="请输入姓名"
              />
            </div>

            <div class="form-group">
              <label for="regPassword" class="form-label">密码</label>
              <div class="password-input-wrapper">
                <input
                  id="regPassword"
                  v-model="registerForm.password"
                  :type="showRegPassword ? 'text' : 'password'"
                  required
                  class="form-input"
                  placeholder="请输入密码"
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="showRegPassword = !showRegPassword"
                >
                  <svg v-if="!showRegPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                </button>
              </div>
            </div>

            <div class="form-group">
              <label for="confirmPassword" class="form-label">确认密码</label>
              <input
                id="confirmPassword"
                v-model="registerForm.confirmPassword"
                type="password"
                required
                class="form-input"
                placeholder="请再次输入密码"
              />
            </div>

            <button
              type="submit"
              :disabled="isLoading || !inviteCodeStatus?.isValid"
              class="login-btn"
            >
              {{ isLoading ? '注册中...' : '注册' }}
            </button>
          </form>

          <div class="register-link">
            <span>已有账号？</span>
            <a href="#" @click.prevent="isLogin = true" class="register-link-text">立即登录</a>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M7 17L17 7M17 7H7M17 7V17"/>
            </svg>
          </div>
        </div>

        <!-- 错误信息 -->
        <div v-if="errorMessage" class="error-message">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          {{ errorMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    
    const isLogin = ref(true)
    const isLoading = ref(false)
    const errorMessage = ref('')
    const inviteCodeStatus = ref(null)
    const showPassword = ref(false)
    const showRegPassword = ref(false)
    const rememberMe = ref(false)
    
    const loginForm = reactive({
      username: '',
      password: ''
    })
    
    const registerForm = reactive({
      inviteCode: '',
      username: '',
      email: '',
      fullName: '',
      password: '',
      confirmPassword: ''
    })
    

    // 验证邀请码
    const validateInviteCode = async () => {
      if (!registerForm.inviteCode) return
      
      try {
        const response = await api.post('/auth/validate-invite', {
          invite_code: registerForm.inviteCode
        })
        inviteCodeStatus.value = response.data
      } catch (error) {
        inviteCodeStatus.value = {
          isValid: false,
          message: '邀请码验证失败'
        }
      }
    }
    
    // 处理登录
    const handleLogin = async () => {
      isLoading.value = true
      errorMessage.value = ''
      
      try {
        const formData = new FormData()
        formData.append('username', loginForm.username)
        formData.append('password', loginForm.password)
        
        const response = await api.post('/auth/login', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        })
        
        // 保存用户信息和token
        userStore.setUser(response.data.user)
        userStore.setToken(response.data.access_token)
        
        // 跳转到仪表板
        router.push('/dashboard')
      } catch (error) {
        errorMessage.value = error.response?.data?.detail || '登录失败'
      } finally {
        isLoading.value = false
      }
    }
    
    // 处理注册
    const handleRegister = async () => {
      if (registerForm.password !== registerForm.confirmPassword) {
        errorMessage.value = '两次输入的密码不一致'
        return
      }
      
      isLoading.value = true
      errorMessage.value = ''
      
      try {
        const response = await api.post('/auth/register', {
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password,
          full_name: registerForm.fullName,
          invite_code: registerForm.inviteCode
        })
        
        // 保存用户信息和token
        userStore.setUser(response.data.user)
        userStore.setToken(response.data.access_token)
        
        // 跳转到仪表板
        router.push('/dashboard')
      } catch (error) {
        errorMessage.value = error.response?.data?.detail || '注册失败'
      } finally {
        isLoading.value = false
      }
    }
    
    return {
      isLogin,
      isLoading,
      errorMessage,
      inviteCodeStatus,
      showPassword,
      showRegPassword,
      rememberMe,
      loginForm,
      registerForm,
      validateInviteCode,
      handleLogin,
      handleRegister
    }
  }
}
</script>

<style scoped>
/* 登录页面样式 - 参考现代设计 */
.login-container {
  min-height: 100vh;
  background: #f8fafc;
  position: relative;
  display: flex;
  flex-direction: column;
}

/* Logo 区域 */
.logo-section {
  position: absolute;
  top: 24px;
  left: 24px;
  z-index: 10;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* 登录表单容器 */
.login-form-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 24px 24px;
}

.login-form-wrapper {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 32px;
}

/* 表单标签 */
.form-tabs {
  display: flex;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 4px;
  margin-bottom: 32px;
}

.tab-button {
  flex: 1;
  padding: 12px 16px;
  border: none;
  background: transparent;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-button.active {
  background: white;
  color: #1e293b;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.tab-button:hover:not(.active) {
  color: #1e293b;
}

/* 表单标题 */
.form-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
  text-align: center;
}

.form-subtitle {
  font-size: 16px;
  color: #64748b;
  margin: 0 0 32px 0;
  text-align: center;
}



/* 表单样式 */
.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  color: #374151;
  background: white;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-input::placeholder {
  color: #9ca3af;
}

/* 密码输入框 */
.password-input-wrapper {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s ease;
}

.password-toggle:hover {
  color: #374151;
}

/* 表单选项 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 8px 0;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox {
  width: 16px;
  height: 16px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  cursor: pointer;
}

.checkbox:checked {
  background: #6366f1;
  border-color: #6366f1;
}

.checkbox-label {
  font-size: 14px;
  color: #374151;
  cursor: pointer;
}

.forgot-password {
  font-size: 14px;
  color: #6366f1;
  text-decoration: none;
  transition: color 0.2s ease;
}

.forgot-password:hover {
  color: #4f46e5;
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  padding: 12px 16px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 8px;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 注册链接 */
.register-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 24px;
  font-size: 14px;
  color: #64748b;
}

.register-link-text {
  color: #6366f1;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.register-link-text:hover {
  color: #4f46e5;
}

/* 表单消息 */
.form-message {
  font-size: 12px;
  margin-top: 4px;
}

.form-message.success {
  color: #059669;
}

.form-message.error {
  color: #dc2626;
}

/* 错误信息 */
.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 14px;
  margin-top: 16px;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-form-wrapper {
    margin: 16px;
    padding: 24px;
  }
  
  .logo-section {
    top: 16px;
    left: 16px;
  }
  
  .logo-text {
    font-size: 20px;
  }
  
  .form-title {
    font-size: 24px;
  }
}

/* 动画效果 */
.login-form,
.register-form {
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 焦点状态优化 */
.form-input:focus,
.login-btn:focus,
.password-toggle:focus {
  outline: 2px solid #6366f1;
  outline-offset: 2px;
}

/* 高对比度模式支持 */
@media (prefers-contrast: high) {
  .form-input {
    border-width: 2px;
  }
  
  .login-btn {
    border: 2px solid #6366f1;
  }
}
</style>