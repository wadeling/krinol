<template>
  <div class="dashboard">
    <Layout>
      <template #header>
        <div class="header-content">
          <h1>仪表板</h1>
          <p>欢迎回来，{{ userStore.user?.username }}！</p>
        </div>
      </template>
      
      <template #content>
        <div class="dashboard-content">
          <!-- 统计卡片 -->
          <el-row :gutter="20" class="stats-row">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon">
                    <el-icon size="24" color="#409EFF">
                      <Document />
                    </el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ resumeStats.total }}</div>
                    <div class="stat-label">总简历数</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon">
                    <el-icon size="24" color="#67C23A">
                      <TrendCharts />
                    </el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ resumeStats.analyzed }}</div>
                    <div class="stat-label">已分析</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon">
                    <el-icon size="24" color="#E6A23C">
                      <Clock />
                    </el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ resumeStats.pending }}</div>
                    <div class="stat-label">待分析</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-content">
                    <div class="stat-icon">
                      <el-icon size="24" color="#F56C6C">
                        <Star />
                      </el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-number">{{ resumeStats.averageScore }}</div>
                      <div class="stat-label">平均评分</div>
                    </div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
          
          <!-- 快速操作 -->
          <el-card class="quick-actions-card">
            <template #header>
              <h3>快速操作</h3>
            </template>
            <div class="quick-actions">
              <el-button type="primary" size="large" @click="$router.push('/resumes')">
                <el-icon><Upload /></el-icon>
                上传简历
              </el-button>
              <el-button type="success" size="large" @click="$router.push('/analysis')">
                <el-icon><TrendCharts /></el-icon>
                查看分析
              </el-button>
              <el-button type="info" size="large" @click="$router.push('/profile')">
                <el-icon><User /></el-icon>
                个人设置
              </el-button>
            </div>
          </el-card>
          
          <!-- 最近活动 -->
          <el-card class="recent-activity-card">
            <template #header>
              <h3>最近活动</h3>
            </template>
            <el-timeline>
              <el-timeline-item
                v-for="activity in recentActivities"
                :key="activity.id"
                :timestamp="activity.timestamp"
                :type="activity.type"
              >
                {{ activity.description }}
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </div>
      </template>
    </Layout>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import Layout from '@/components/Layout.vue'
import { useUserStore } from '@/stores/user'
import { useResumeStore } from '@/stores/resume'
import { useAnalysisStore } from '@/stores/analysis'

const userStore = useUserStore()
const resumeStore = useResumeStore()
const analysisStore = useAnalysisStore()

const resumeStats = ref({
  total: 0,
  analyzed: 0,
  pending: 0,
  averageScore: 0
})

const recentActivities = ref([
  {
    id: 1,
    description: '上传了新的简历文件',
    timestamp: '2024-01-15 10:30',
    type: 'primary'
  },
  {
    id: 2,
    description: '完成了简历分析',
    timestamp: '2024-01-15 09:15',
    type: 'success'
  },
  {
    id: 3,
    description: '登录系统',
    timestamp: '2024-01-15 08:00',
    type: 'info'
  }
])

onMounted(async () => {
  await loadDashboardData()
})

const loadDashboardData = async () => {
  try {
    await Promise.all([
      resumeStore.fetchResumes(),
      analysisStore.fetchAnalyses()
    ])
    
    // 计算统计数据
    resumeStats.value.total = resumeStore.resumes.length
    resumeStats.value.analyzed = analysisStore.analyses.filter(a => a.status === 'completed').length
    resumeStats.value.pending = analysisStore.analyses.filter(a => a.status === 'pending').length
    
    const completedAnalyses = analysisStore.analyses.filter(a => a.status === 'completed' && a.overall_score)
    if (completedAnalyses.length > 0) {
      resumeStats.value.averageScore = Math.round(
        completedAnalyses.reduce((sum, a) => sum + a.overall_score, 0) / completedAnalyses.length
      )
    }
  } catch (error) {
    console.error('加载仪表板数据失败:', error)
  }
}
</script>

<style lang="scss" scoped>
.dashboard {
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

.dashboard-content {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  .stat-content {
    display: flex;
    align-items: center;
    
    .stat-icon {
      margin-right: 16px;
      padding: 12px;
      background-color: #f0f9ff;
      border-radius: 8px;
    }
    
    .stat-info {
      .stat-number {
        font-size: 24px;
        font-weight: bold;
        color: #333;
        margin-bottom: 4px;
      }
      
      .stat-label {
        font-size: 14px;
        color: #666;
      }
    }
  }
}

.quick-actions-card {
  margin-bottom: 20px;
  
  .quick-actions {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    
    .el-button {
      flex: 1;
      min-width: 120px;
    }
  }
}

.recent-activity-card {
  .el-timeline {
    padding-left: 0;
  }
}
</style>
