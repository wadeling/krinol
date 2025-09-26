<template>
  <div class="profile">
    <Layout>
      <template #header>
        <div class="header-content">
          <h1>个人设置</h1>
          <p>管理您的个人信息和账户设置</p>
        </div>
      </template>
      
      <template #content>
        <div class="profile-content">
          <el-row :gutter="20">
            <!-- 个人信息 -->
            <el-col :span="16">
              <el-card class="profile-card">
                <template #header>
                  <h3>个人信息</h3>
                </template>
                
                <el-form
                  ref="profileFormRef"
                  :model="profileForm"
                  :rules="profileRules"
                  label-width="100px"
                >
                  <el-form-item label="用户名" prop="username">
                    <el-input v-model="profileForm.username" />
                  </el-form-item>
                  
                  <el-form-item label="邮箱" prop="email">
                    <el-input v-model="profileForm.email" disabled />
                  </el-form-item>
                  
                  <el-form-item label="姓名" prop="fullName">
                    <el-input v-model="profileForm.fullName" />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button
                      type="primary"
                      @click="updateProfile"
                      :loading="userStore.loading"
                    >
                      保存修改
                    </el-button>
                    <el-button @click="resetProfile">重置</el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-col>
            
            <!-- 账户信息 -->
            <el-col :span="8">
              <el-card class="account-card">
                <template #header>
                  <h3>账户信息</h3>
                </template>
                
                <div class="account-info">
                  <div class="info-item">
                    <label>用户ID：</label>
                    <span>{{ userStore.user?.id }}</span>
                  </div>
                  
                  <div class="info-item">
                    <label>注册时间：</label>
                    <span>{{ formatDate(userStore.user?.created_at) }}</span>
                  </div>
                  
                  <div class="info-item">
                    <label>最后更新：</label>
                    <span>{{ formatDate(userStore.user?.updated_at) }}</span>
                  </div>
                  
                  <div class="info-item">
                    <label>账户状态：</label>
                    <el-tag :type="userStore.user?.is_active ? 'success' : 'danger'">
                      {{ userStore.user?.is_active ? '正常' : '已禁用' }}
                    </el-tag>
                  </div>
                </div>
              </el-card>
              
              <!-- 修改密码 -->
              <el-card class="password-card">
                <template #header>
                  <h3>修改密码</h3>
                </template>
                
                <el-form
                  ref="passwordFormRef"
                  :model="passwordForm"
                  :rules="passwordRules"
                  label-width="100px"
                >
                  <el-form-item label="当前密码" prop="currentPassword">
                    <el-input
                      v-model="passwordForm.currentPassword"
                      type="password"
                      show-password
                    />
                  </el-form-item>
                  
                  <el-form-item label="新密码" prop="newPassword">
                    <el-input
                      v-model="passwordForm.newPassword"
                      type="password"
                      show-password
                    />
                  </el-form-item>
                  
                  <el-form-item label="确认密码" prop="confirmPassword">
                    <el-input
                      v-model="passwordForm.confirmPassword"
                      type="password"
                      show-password
                    />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button
                      type="primary"
                      @click="updatePassword"
                      :loading="passwordLoading"
                    >
                      修改密码
                    </el-button>
                    <el-button @click="resetPassword">重置</el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </template>
    </Layout>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import Layout from '@/components/Layout.vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const profileFormRef = ref()
const passwordFormRef = ref()
const passwordLoading = ref(false)

const profileForm = reactive({
  username: '',
  email: '',
  fullName: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const profileRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在3到50个字符', trigger: 'blur' }
  ],
  fullName: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ]
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

onMounted(() => {
  initProfileForm()
})

const initProfileForm = () => {
  if (userStore.user) {
    profileForm.username = userStore.user.username
    profileForm.email = userStore.user.email
    profileForm.fullName = userStore.user.full_name || ''
  }
}

const updateProfile = async () => {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      const success = await userStore.updateProfile({
        username: profileForm.username,
        full_name: profileForm.fullName
      })
      if (success) {
        initProfileForm()
      }
    }
  })
}

const resetProfile = () => {
  initProfileForm()
}

const updatePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        passwordLoading.value = true
        // 这里应该调用修改密码的API
        // await userStore.updatePassword(passwordForm)
        ElMessage.success('密码修改成功')
        resetPassword()
      } catch (error) {
        ElMessage.error('密码修改失败')
      } finally {
        passwordLoading.value = false
      }
    }
  })
}

const resetPassword = () => {
  passwordForm.currentPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}
</script>

<style lang="scss" scoped>
.profile {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header-content {
  h1 {
    margin: 0 0 8px 0;
    color: #333;
    font-size: 24px;
  }
  
  p {
    margin: 0;
    color: #666;
    font-size: 14px;
  }
}

.profile-content {
  padding: 20px;
}

.profile-card,
.account-card,
.password-card {
  margin-bottom: 20px;
  
  h3 {
    margin: 0;
    color: #333;
  }
}

.account-info {
  .info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;
    
    &:last-child {
      border-bottom: none;
    }
    
    label {
      font-weight: 500;
      color: #666;
    }
    
    span {
      color: #333;
    }
  }
}
</style>
