<template>
  <div class="not-found">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <div class="error-message">页面不存在</div>
      <div class="error-description">
        抱歉，您访问的页面不存在或已被删除
      </div>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">
          返回首页
        </el-button>
        <el-button @click="goBack">
          返回上页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/dashboard')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style lang="scss" scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.not-found-content {
  text-align: center;
  color: white;
  
  .error-code {
    font-size: 120px;
    font-weight: bold;
    margin-bottom: 20px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
  
  .error-message {
    font-size: 32px;
    margin-bottom: 16px;
    font-weight: 500;
  }
  
  .error-description {
    font-size: 16px;
    margin-bottom: 40px;
    opacity: 0.9;
  }
  
  .error-actions {
    .el-button {
      margin: 0 8px;
      padding: 12px 24px;
      font-size: 16px;
    }
  }
}
</style>
