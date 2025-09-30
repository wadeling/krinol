<template>
  <div class="dashboard-container">
    <!-- Top Nav -->
    <header class="header">
      <div class="header-content">
        <div class="header-inner">
          <!-- Brand -->
          <div class="brand">
            <div class="brand-text">Krinol</div>
          </div>


          <!-- Right side -->
          <div class="header-right">
            <!-- Quick search / Q -->
            <button class="quick-search-btn" title="Quick Search">
              Q
            </button>
            <!-- Language + user -->
            <div class="user-info">
              <span class="lang-tag">EN</span>
              <span class="hello-tag">Hello,</span>
              <span class="username">{{ userStore.user?.username || 'User' }}</span>
              <button 
                @click="handleLogout"
                class="logout-btn"
              >
                退出
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main -->
    <main class="main-content">
      <!-- Quick actions -->
      <section class="quick-actions">
        <!-- Resume attachment -->
        <div class="action-card" @click="showUploadModal = true">
          <div class="action-icon resume-icon">▣</div>
          <div class="action-content">
            <div class="action-title">Resume attachment</div>
            <div class="action-subtitle">Import attachments from email</div>
          </div>
        </div>
        
        <!-- Batch analysis -->
        <div class="action-card" @click="$router.push('/analysis')">
          <div class="action-icon analysis-icon">▥</div>
          <div class="action-content">
            <div class="action-title">Batch analysis</div>
            <div class="action-subtitle">Parse multiple CVs</div>
          </div>
        </div>
      </section>


      <!-- Content grid: table left, charts right -->
      <section class="content-grid">
        <!-- Left: table -->
        <div class="table-container">
          <div class="card table-card">
            <!-- Table header -->
            <div class="table-header">
              Candidates
            </div>
            <div class="table-wrapper scrollbar-thin">
              <table class="candidates-table">
                <thead>
                  <tr class="table-head-row">
                    <th class="table-header-cell">Name</th>
                    <th class="table-header-cell">Phone</th>
                    <th class="table-header-cell">Company</th>
                    <th class="table-header-cell">Position</th>
                    <th class="table-header-cell">Location</th>
                    <th class="table-header-cell">Working time</th>
                    <th class="table-header-cell">CV Score</th>
                    <th class="table-header-cell">Operation</th>
                  </tr>
                </thead>
                <tbody class="table-body">
                  <!-- Sample data -->
                  <tr class="table-row" v-for="candidate in candidates" :key="candidate.id">
                    <td class="table-cell name-cell">{{ candidate.name }}</td>
                    <td class="table-cell phone-cell">{{ candidate.phone }}</td>
                    <td class="table-cell company-cell">{{ candidate.company }}</td>
                    <td class="table-cell position-cell">{{ candidate.position }}</td>
                    <td class="table-cell location-cell">{{ candidate.location }}</td>
                    <td class="table-cell working-time-cell">{{ candidate.workingTime }}</td>
                    <td class="table-cell score-cell">
                      <span class="score-badge" :class="getScoreClass(candidate.cvScore)">
                        {{ candidate.cvScore }}/100
                      </span>
                    </td>
                    <td class="table-cell operation-cell">
                      <div class="operation-buttons">
                        <button class="add-talent-btn">Add to talent pool</button>
                        <span class="status-chip" :class="getStatusClass(candidate.status)">{{ candidate.status }}</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Right: charts and side panel -->
        <aside class="charts-container">
          <!-- Chart 1 -->
          <div class="card chart-card">
            <div class="chart-title">Candidate Status Analysis</div>
            <div class="chart-content">
              <!-- Donut -->
              <div class="chart-donut">
                <svg viewBox="0 0 36 36" class="donut-svg">
                  <!-- base track -->
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#E5E7EB" stroke-width="7"></circle>
                  <!-- arcs (fake data proportions) -->
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#22c55e" stroke-width="7" stroke-dasharray="22 90" stroke-dashoffset="0"></circle>
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#f97316" stroke-width="7" stroke-dasharray="15 97" stroke-dashoffset="-22"></circle>
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#38bdf8" stroke-width="7" stroke-dasharray="18 94" stroke-dashoffset="-37"></circle>
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#a78bfa" stroke-width="7" stroke-dasharray="10 102" stroke-dashoffset="-55"></circle>
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#ef4444" stroke-width="7" stroke-dasharray="12 100" stroke-dashoffset="-65"></circle>
                </svg>
                <div class="donut-center ring-soft"></div>
              </div>
              <!-- Legend -->
              <ul class="chart-legend">
                <li class="legend-item"><span class="legend-dot emerald-dot"></span> 初步沟通</li>
                <li class="legend-item"><span class="legend-dot orange-dot"></span> 面试安排</li>
                <li class="legend-item"><span class="legend-dot sky-dot"></span> 简历推荐</li>
                <li class="legend-item"><span class="legend-dot violet-dot"></span> Offer</li>
                <li class="legend-item"><span class="legend-dot red-dot"></span> 入职</li>
                <li class="legend-item"><span class="legend-dot blue-dot"></span> 淘汰</li>
              </ul>
            </div>
          </div>

          <!-- Chart 2 -->
          <div class="card chart-card">
            <div class="chart-title">Position Status Analysis</div>
            <div class="chart-content">
              <div class="chart-donut">
                <svg viewBox="0 0 36 36" class="donut-svg">
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#E5E7EB" stroke-width="7"></circle>
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#10b981" stroke-width="7" stroke-dasharray="40 72" stroke-dashoffset="0"></circle>
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#f59e0b" stroke-width="7" stroke-dasharray="25 87" stroke-dashoffset="-40"></circle>
                  <circle cx="18" cy="18" r="14.5" fill="none" stroke="#ef4444" stroke-width="7" stroke-dasharray="15 97" stroke-dashoffset="-65"></circle>
                </svg>
                <div class="donut-center ring-soft"></div>
              </div>
              <ul class="chart-legend">
                <li class="legend-item"><span class="legend-dot emerald-dot"></span> 已开始</li>
                <li class="legend-item"><span class="legend-dot amber-dot"></span> 进行中</li>
                <li class="legend-item"><span class="legend-dot rose-dot"></span> 已完成</li>
              </ul>
            </div>
          </div>

        </aside>
      </section>
    </main>

    <!-- File Upload Modal -->
    <FileUploadModal 
      v-model:visible="showUploadModal" 
      @upload-success="handleUploadSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import FileUploadModal from '@/components/FileUploadModal.vue'

const router = useRouter()
const userStore = useUserStore()

// 文件上传弹窗状态
const showUploadModal = ref(false)

// 示例候选人数据
const candidates = ref([
  {
    id: 1,
    name: 'Rick',
    phone: '156662781098',
    company: '用友软件股份有限公司苏州分公司',
    position: '销售工程师',
    location: '江苏-苏州',
    workingTime: '7',
    cvScore: 85,
    status: 'Deprecated'
  },
  {
    id: 2,
    name: 'Sarah',
    phone: '13812345678',
    company: '腾讯科技（深圳）有限公司',
    position: '前端开发工程师',
    location: '广东-深圳',
    workingTime: '5',
    cvScore: 92,
    status: 'Active'
  },
  {
    id: 3,
    name: 'Mike',
    phone: '13987654321',
    company: '阿里巴巴（中国）有限公司',
    position: '产品经理',
    location: '浙江-杭州',
    workingTime: '8',
    cvScore: 78,
    status: 'Pending'
  },
  {
    id: 4,
    name: 'Lisa',
    phone: '13765432109',
    company: '字节跳动科技有限公司',
    position: 'UI设计师',
    location: '北京-朝阳',
    workingTime: '3',
    cvScore: 88,
    status: 'Active'
  }
])

// 根据分数返回对应的样式类
const getScoreClass = (score) => {
  if (score >= 90) return 'score-excellent'
  if (score >= 80) return 'score-good'
  if (score >= 70) return 'score-average'
  return 'score-poor'
}

// 根据状态返回对应的样式类
const getStatusClass = (status) => {
  switch (status) {
    case 'Deprecated':
      return 'status-deprecated'
    case 'Active':
      return 'status-active'
    case 'Pending':
      return 'status-pending'
    default:
      return 'status-default'
  }
}

// 处理文件上传成功
const handleUploadSuccess = (response) => {
  console.log('文件上传成功:', response)
  // 这里可以添加成功提示或其他逻辑
  // 比如刷新候选人列表等
}

// 退出登录
const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

onMounted(() => {
  // 初始化数据
})
</script>

<style lang="scss" scoped>
/* Dashboard样式 - 完全参考HTML文件 */

/* 主容器 */
.dashboard-container {
  min-height: 100vh;
  background-color: #f8fafc;
  color: #334155;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .quick-actions {
    grid-template-columns: 1fr;
  }
  
  .table-wrapper {
    overflow-x: auto;
  }
  
  .candidates-table {
    min-width: 600px;
  }
}

/* 头部样式 */
.header {
  background-color: white;
  border-bottom: 1px solid #e2e8f0;
}

.header-content {
  max-width: 80rem;
  margin: 0 auto;
  padding: 0 1rem;
}

.header-inner {
  display: flex;
  align-items: center;
  height: 4rem;
  gap: 1rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand-text {
  font-size: 1.5rem;
  font-weight: 900;
  color: #1e293b;
}


.header-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.quick-search-btn {
  height: 2.25rem;
  width: 2.25rem;
  display: grid;
  place-items: center;
  border-radius: 0.5rem;
  background-color: #f1f5f9;
  border: none;
  color: #475569;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: #e2e8f0;
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.lang-tag, .hello-tag {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  background-color: #f1f5f9;
}

.username {
  font-weight: 500;
}

.logout-btn {
  margin-left: 0.5rem;
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  background-color: #f1f5f9;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: #e2e8f0;
  }
}

/* 主内容区域 */
.main-content {
  max-width: 80rem;
  margin: 0 auto;
  padding: 1.5rem 1rem;
}

/* 快速操作区域 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

@media (max-width: 768px) {
  .quick-actions {
    grid-template-columns: 1fr;
  }
}


/* 内容网格布局 - 参考HTML文件 */
.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  margin-top: 0.75rem;
}

@media (min-width: 1024px) {
  .content-grid {
    grid-template-columns: 2fr 1fr;
  }
}

/* 表格容器 */
.table-container {
  width: 100%;
}

.table-card {
  overflow: hidden;
}

.table-header {
  background-color: rgba(241, 245, 249, 0.7);
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
}

.table-wrapper {
  overflow: auto;
}

.candidates-table {
  width: 100%;
  font-size: 0.875rem;
}

.table-head-row {
  background-color: #f8fafc;
  color: #64748b;
}

.table-header-cell {
  text-align: left;
  font-weight: 500;
  padding: 0.75rem 1rem;
}

.table-body {
  border-top: 1px solid #f1f5f9;
}

.table-row {
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.2s;
}

.table-row:hover {
  background-color: #f8fafc;
}

.table-cell {
  padding: 0.75rem 1rem;
  vertical-align: middle;
}

.name-cell {
  color: #0ea5e9;
}

.phone-cell, .working-time-cell {
  color: #64748b;
}

.score-cell {
  text-align: center;
}

.company-cell {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.operation-buttons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.add-talent-btn {
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  background-color: #1e293b;
  color: white;
  font-size: 0.75rem;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: #334155;
  }
}

.status-chip {
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-weight: 500;
  
  &.status-deprecated {
    background-color: #fef3c7;
    color: #92400e;
  }
  
  &.status-active {
    background-color: #dcfce7;
    color: #166534;
  }
  
  &.status-pending {
    background-color: #dbeafe;
    color: #1e40af;
  }
  
  &.status-default {
    background-color: #f1f5f9;
    color: #64748b;
  }
}

/* CV Score 样式 */
.score-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  font-weight: 600;
  display: inline-block;
  
  &.score-excellent {
    background-color: #dcfce7;
    color: #166534;
  }
  
  &.score-good {
    background-color: #dbeafe;
    color: #1e40af;
  }
  
  &.score-average {
    background-color: #fef3c7;
    color: #92400e;
  }
  
  &.score-poor {
    background-color: #fee2e2;
    color: #991b1b;
  }
}

/* 图表容器 */
.charts-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}


.chart-card {
  padding: 1rem;
}

.chart-title {
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.chart-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.chart-donut {
  position: relative;
  height: 7rem;
  width: 7rem;
  flex-shrink: 0;
}

.donut-svg {
  height: 7rem;
  width: 7rem;
}

.donut-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  height: 3.5rem;
  width: 3.5rem;
  border-radius: 50%;
  background-color: white;
}

.chart-legend {
  list-style: none;
  margin: 0;
  padding: 0;
  font-size: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.legend-dot {
  height: 0.5rem;
  width: 0.5rem;
  border-radius: 50%;
}

.emerald-dot {
  background-color: #10b981;
}

.orange-dot {
  background-color: #f97316;
}

.sky-dot {
  background-color: #38bdf8;
}

.violet-dot {
  background-color: #a78bfa;
}

.red-dot {
  background-color: #ef4444;
}

.blue-dot {
  background-color: #2563eb;
}

.amber-dot {
  background-color: #f59e0b;
}

.rose-dot {
  background-color: #f43f5e;
}

.action-card {
  background-color: white;
  border-radius: 0.75rem;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  box-shadow: 
    0 10px 15px -3px rgba(0,0,0,0.08),
    0 4px 6px -2px rgba(0,0,0,0.03);
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: 
      0 20px 25px -5px rgba(0,0,0,0.1),
      0 10px 10px -5px rgba(0,0,0,0.04);
    transform: translateY(-1px);
  }
}

.action-icon {
  height: 3rem;
  width: 3rem;
  border-radius: 1rem;
  display: grid;
  place-items: center;
  font-size: 1.25rem;
}

.resume-icon {
  background-color: #e0f2fe;
  color: #0ea5e9;
}

.analysis-icon {
  background-color: #dcfce7;
  color: #10b981;
}

.action-content {
  flex: 1;
}

.action-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.action-subtitle {
  font-size: 0.75rem;
  color: #64748b;
}

/* 卡片样式 */
.card {
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 
    0 10px 15px -3px rgba(0,0,0,0.08),
    0 4px 6px -2px rgba(0,0,0,0.03);
}

/* 环形装饰样式 */
.ring-soft {
  box-shadow: inset 0 0 0 10px rgba(255,255,255,1);
}

/* 滚动条样式 */
.scrollbar-thin {
  &::-webkit-scrollbar { 
    height: 8px; 
    width: 8px; 
  }
  
  &::-webkit-scrollbar-thumb { 
    background: #D1D5DB; 
    border-radius: 8px; 
  }
  
  &::-webkit-scrollbar-track { 
    background: transparent; 
  }
}

/* 分数标签样式 */
.score-badge {
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-weight: 500;
  
  &.score-excellent {
    background-color: #dcfce7;
    color: #166534;
  }
  
  &.score-good {
    background-color: #dbeafe;
    color: #1e40af;
  }
  
  &.score-average {
    background-color: #fef3c7;
    color: #92400e;
  }
  
  &.score-poor {
    background-color: #fee2e2;
    color: #991b1b;
  }
}
</style>
