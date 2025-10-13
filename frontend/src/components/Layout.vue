<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <div class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div v-if="!sidebarCollapsed" class="brand-container">
          <h2>Krinol</h2>
          <p class="brand-slogan">智能筛选，精准判断</p>
        </div>
        <el-icon v-else size="24" color="#409EFF">
          <Document />
        </el-icon>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="sidebarCollapsed"
        :unique-opened="true"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <span>仪表板</span>
        </el-menu-item>
        
        <el-menu-item index="/resumes">
          <el-icon><Document /></el-icon>
          <span>简历管理</span>
        </el-menu-item>
        
        <el-menu-item index="/analysis">
          <el-icon><TrendCharts /></el-icon>
          <span>分析结果</span>
        </el-menu-item>
        
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>个人设置</span>
        </el-menu-item>
      </el-menu>
    </div>
    
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 顶部导航栏 -->
      <div class="topbar">
        <div class="topbar-left">
          <el-button
            type="text"
            @click="toggleSidebar"
            class="sidebar-toggle"
          >
            <el-icon size="20">
              <Fold v-if="!sidebarCollapsed" />
              <Expand v-else />
            </el-icon>
          </el-button>
        </div>
        
        <div class="topbar-right">
          <el-dropdown @command="handleUserCommand">
            <div class="user-info">
              <el-avatar :size="32" :src="userStore.user?.avatar">
                {{ userStore.user?.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="username">{{ userStore.user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人设置
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      
      <!-- 页面内容 -->
      <div class="page-content">
        <slot name="header" v-if="$slots.header">
          <div class="page-header">
            <slot name="header"></slot>
          </div>
        </slot>
        
        <div class="page-body">
          <slot name="content">
            <router-view />
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const sidebarCollapsed = ref(false)

const activeMenu = computed(() => route.path)

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const handleUserCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        userStore.logout()
        router.push('/login')
      } catch {
        // 用户取消
      }
      break
  }
}
</script>

<style lang="scss" scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.sidebar {
  width: 240px;
  background-color: #304156;
  transition: width 0.3s;
  
  &.collapsed {
    width: 64px;
  }
  
  .sidebar-header {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid #434a50;
    
    .brand-container {
      text-align: center;
      
      h2 {
        color: white;
        margin: 0 0 2px 0;
        font-size: 18px;
        font-weight: 700;
        line-height: 1;
      }
      
      .brand-slogan {
        color: #bfcbd9;
        margin: 0;
        font-size: 10px;
        font-weight: 500;
        line-height: 1;
        letter-spacing: 0.025em;
      }
    }
  }
  
  .sidebar-menu {
    border: none;
    background-color: #304156;
    
    :deep(.el-menu-item) {
      color: #bfcbd9;
      
      &:hover {
        background-color: #263445;
        color: white;
      }
      
      &.is-active {
        background-color: #409EFF;
        color: white;
      }
    }
  }
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar {
  height: 60px;
  background-color: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  
  .topbar-left {
    .sidebar-toggle {
      border: none;
      background: none;
      padding: 8px;
      
      &:hover {
        background-color: #f5f7fa;
      }
    }
  }
  
  .topbar-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 8px 12px;
      border-radius: 4px;
      transition: background-color 0.3s;
      
      &:hover {
        background-color: #f5f7fa;
      }
      
      .username {
        font-size: 14px;
        color: #333;
      }
    }
  }
}

.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.page-header {
  background-color: white;
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.page-body {
  flex: 1;
  padding: 20px;
}
</style>
