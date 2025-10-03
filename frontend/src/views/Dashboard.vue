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
            <div class="action-subtitle">Upload resume attachments</div>
          </div>
        </div>
        
        <!-- Batch analysis -->
        <div class="action-card action-card-disabled">
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
                    <th class="table-header-cell">Position</th>
                    <th class="table-header-cell">School</th>
                    <th class="table-header-cell">Graduation Year</th>
                    <th class="table-header-cell">City</th>
                    <th class="table-header-cell">Email</th>
                    <th class="table-header-cell">CV Score</th>
                    <th class="table-header-cell">Operation</th>
                  </tr>
                </thead>
                <tbody class="table-body">
                  <!-- Sample data -->
                  <tr class="table-row" v-for="candidate in candidates" :key="candidate.id">
                    <td class="table-cell name-cell">{{ candidate.name || 'N/A' }}</td>
                    <td class="table-cell phone-cell">{{ candidate.phone || 'N/A' }}</td>
                    <td class="table-cell position-cell">{{ candidate.position || 'N/A' }}</td>
                    <td class="table-cell company-cell">{{ candidate.school_name || 'N/A' }}</td>
                    <td class="table-cell graduation-year-cell">{{ candidate.graduation_year || 'N/A' }}</td>
                    <td class="table-cell location-cell">{{ candidate.school_city || 'N/A' }}</td>
                    <td class="table-cell working-time-cell">{{ candidate.email || 'N/A' }}</td>
                    <td class="table-cell score-cell">
                      <div class="score-container">
                        <span class="score-badge" :class="getScoreClass(candidate.cvScore)">
                          {{ candidate.cvScore || 0 }}/48
                        </span>
                        <button 
                          v-if="candidate.scoreDetail" 
                          class="score-detail-btn" 
                          @click="showScoreDetail(candidate)"
                          title="查看详细评分"
                        >
                          📊
                        </button>
                      </div>
                    </td>
                    <td class="table-cell operation-cell">
                      <div class="operation-buttons">
                        <button class="add-talent-btn">Add to talent pool</button>
                        <span class="status-chip" :class="getStatusClass(candidate.status)">{{ candidate.status || 'Unknown' }}</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- 分页控件 -->
            <div class="pagination-container">
              <div class="pagination-info">
                <span class="pagination-text">
                  显示 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, totalCandidates) }} 条，共 {{ totalCandidates }} 条记录
                </span>
                <div class="page-size-selector">
                  <label for="pageSize">每页显示：</label>
                  <select id="pageSize" v-model="pageSize" @change="handlePageSizeChange" class="page-size-select">
                    <option value="5">5</option>
                    <option value="10">10</option>
                    <option value="20">20</option>
                    <option value="50">50</option>
                  </select>
                </div>
              </div>
              
              <div class="pagination-controls">
                <button 
                  class="pagination-btn" 
                  :disabled="currentPage === 1"
                  @click="handlePageChange(currentPage - 1)"
                >
                  上一页
                </button>
                
                <div class="page-numbers">
                  <button 
                    v-for="page in getVisiblePages()" 
                    :key="page"
                    class="page-number"
                    :class="{ 
                      active: page === currentPage,
                      ellipsis: page === '...'
                    }"
                    @click="page !== '...' && handlePageChange(page)"
                  >
                    {{ page }}
                  </button>
                </div>
                
                <button 
                  class="pagination-btn" 
                  :disabled="currentPage === totalPages"
                  @click="handlePageChange(currentPage + 1)"
                >
                  下一页
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: charts and side panel -->
        <aside class="charts-container">
          <!-- Charts removed -->
        </aside>
      </section>
    </main>

    <!-- File Upload Modal -->
    <FileUploadModal 
      v-model:visible="showUploadModal" 
      @upload-success="handleUploadSuccess"
    />

    <!-- Score Detail Modal -->
    <div v-if="showScoreDetailModal" class="modal-overlay" @click="closeScoreDetailModal">
      <div class="score-detail-modal" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">评分详情</h3>
          <button class="modal-close" @click="closeScoreDetailModal">×</button>
        </div>
        <div class="modal-content">
          <div class="candidate-info">
            <h4>{{ currentCandidate?.name }}</h4>
            <div class="total-score">
              <span class="score-label">总分：</span>
              <span class="score-value" :class="getScoreClass(currentCandidate?.cvScore)">
                {{ currentCandidate?.cvScore || 0 }}/48
              </span>
            </div>
          </div>
          
          <div class="score-breakdown">
            <h5>各维度得分：</h5>
            <div v-if="!currentScoreDetail" class="no-data">
              暂无评分详情数据
            </div>
            <div v-else class="score-items">
              <div 
                v-for="(detail, key) in currentScoreDetail" 
                :key="key"
                class="score-item"
              >
                <div class="score-item-header">
                  <span class="score-item-name">{{ getScoreItemName(key) }}</span>
                  <span class="score-item-points">{{ detail.score }}分</span>
                </div>
                <div class="score-item-reason">{{ detail.reason }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useResumeStore } from '@/stores/resume'
import FileUploadModal from '@/components/FileUploadModal.vue'

const router = useRouter()
const userStore = useUserStore()
const resumeStore = useResumeStore()

// 文件上传弹窗状态
const showUploadModal = ref(false)

// 候选人数据 - 从简历数据转换而来
const candidates = ref([])

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(10) // 每页显示10条记录
const totalCandidates = ref(0)

// 评分详情弹窗状态
const showScoreDetailModal = ref(false)
const currentScoreDetail = ref(null)
const currentCandidate = ref(null)

// 根据分数返回对应的样式类（满分48分）
const getScoreClass = (score) => {
  if (score >= 40) return 'score-excellent'  // 40分以上为优秀
  if (score >= 30) return 'score-good'       // 30-39分为良好
  if (score >= 20) return 'score-average'    // 20-29分为一般
  return 'score-poor'                        // 20分以下为较差
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

// 获取候选人数据
const fetchCandidates = async (page = 1, size = 10) => {
  try {
    await resumeStore.fetchResumes(page, size)
    
    // 将简历数据转换为候选人数据格式
    candidates.value = (resumeStore.resumes || []).map(resume => ({
      id: resume.id,
      name: resume.name || 'N/A',
      phone: resume.phone || 'N/A',
      position: resume.position || 'N/A',
      school_name: resume.school_name || 'N/A',
      graduation_year: resume.graduation_year || 'N/A',
      school_city: resume.school_city || 'N/A',
      email: resume.email || 'N/A',
      cvScore: resume.score || 0, // 使用数据库中的评分
      scoreDetail: resume.score_detail || null, // 详细评分信息
      status: getResumeStatus(resume) // 根据简历状态确定候选人状态
    }))
    
    // 更新分页信息
    currentPage.value = page
    pageSize.value = size
    totalCandidates.value = resumeStore.pagination?.total || 0
  } catch (error) {
    console.error('获取候选人数据失败:', error)
  }
}

// 计算总页数
const totalPages = computed(() => {
  return resumeStore.pagination?.totalPages || 0
})

// 分页相关方法
const handlePageChange = (page) => {
  currentPage.value = page
  fetchCandidates(page, pageSize.value)
}

const handlePageSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1 // 重置到第一页
  fetchCandidates(1, size)
}

// 获取可见的页码数组
const getVisiblePages = () => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 7) {
    // 如果总页数少于等于7页，显示所有页码
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // 如果总页数大于7页，显示省略号逻辑
    if (current <= 4) {
      // 当前页在前4页
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 3) {
      // 当前页在后4页
      pages.push(1)
      pages.push('...')
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      // 当前页在中间
      pages.push(1)
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    }
  }
  
  return pages
}


// 根据简历状态确定候选人状态
const getResumeStatus = (resume) => {
  if (resume.processing_status === 'completed') return 'Active'
  if (resume.processing_status === 'failed') return 'Deprecated'
  return 'Pending'
}

// 显示评分详情
const showScoreDetail = (candidate) => {
  if (!candidate.scoreDetail) {
    console.log('No score detail found for candidate:', candidate)
    return
  }
  
  console.log('Score detail data:', candidate.scoreDetail)
  console.log('Score detail keys:', Object.keys(candidate.scoreDetail))
  
  currentCandidate.value = candidate
  // 强制创建一个新的对象来触发响应式更新
  currentScoreDetail.value = { ...candidate.scoreDetail }
  showScoreDetailModal.value = true
  
  // 延迟检查数据是否正确设置
  setTimeout(() => {
    console.log('Current score detail after setting:', currentScoreDetail.value)
    console.log('Keys after setting:', Object.keys(currentScoreDetail.value))
  }, 100)
}

// 关闭评分详情弹窗
const closeScoreDetailModal = () => {
  showScoreDetailModal.value = false
  currentScoreDetail.value = null
  currentCandidate.value = null
}

// 获取评分项目名称
const getScoreItemName = (key) => {
  const scoreNames = {
    region_score: '地域筛选',
    school_score: '学校选择', 
    major_score: '专业匹配',
    highlight_score: '个人亮点',
    experience_score: '项目经历',
    quality_score: '简历质量'
  }
  return scoreNames[key] || key
}

// 检查是否有有效的评分项目
const hasValidScoreItems = computed(() => {
  if (!currentScoreDetail.value) return false
  return Object.keys(currentScoreDetail.value).length > 0
})

// 处理文件上传成功
const handleUploadSuccess = async (response) => {
  console.log('文件上传成功:', response)
  // 刷新候选人列表
  try {
    await fetchCandidates()
  } catch (error) {
    console.error('刷新候选人列表失败:', error)
  }
}

// 退出登录
const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

onMounted(async () => {
  // 初始化数据
  try {
    await fetchCandidates()
  } catch (error) {
    console.error('初始化候选人数据失败:', error)
  }
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
    grid-template-columns: 1fr;
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

.position-cell {
  color: #059669;
  font-weight: 500;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.score-cell {
  text-align: center;
}

.company-cell {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 分页组件样式 */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.pagination-text {
  color: #64748b;
  font-size: 0.875rem;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-size-selector label {
  color: #64748b;
  font-size: 0.875rem;
}

.page-size-select {
  padding: 0.25rem 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background-color: white;
  font-size: 0.875rem;
  color: #374151;
}

.page-size-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background-color: white;
  color: #374151;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.page-number {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  background-color: white;
  color: #374151;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 2.5rem;
  text-align: center;
}

.page-number:hover {
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

.page-number.active {
  background-color: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.page-number.active:hover {
  background-color: #2563eb;
  border-color: #2563eb;
}

/* 省略号样式 */
.page-number.ellipsis {
  cursor: default;
  border: none;
  background: none;
  color: #9ca3af;
}

.page-number.ellipsis:hover {
  background: none;
  border: none;
  color: #9ca3af;
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

.action-card-disabled {
  cursor: default;
  opacity: 0.6;
  
  &:hover {
    box-shadow: 
      0 10px 15px -3px rgba(0,0,0,0.08),
      0 4px 6px -2px rgba(0,0,0,0.03);
    transform: none;
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

/* 评分容器样式 */
.score-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.score-detail-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: #f3f4f6;
  }
}

/* 评分详情弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.score-detail-modal {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 
    0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 1.5rem 0 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 1.5rem;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: #f3f4f6;
    color: #374151;
  }
}

.modal-content {
  padding: 0 1.5rem 1.5rem 1.5rem;
  overflow-y: auto;
  max-height: calc(80vh - 120px);
}

.candidate-info {
  margin-bottom: 1.5rem;
  
  h4 {
    font-size: 1.125rem;
    font-weight: 600;
    color: #111827;
    margin: 0 0 0.75rem 0;
  }
}

.total-score {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.score-label {
  font-weight: 500;
  color: #6b7280;
}

.score-value {
  font-size: 1.25rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  
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

.score-breakdown {
  h5 {
    font-size: 1rem;
    font-weight: 600;
    color: #111827;
    margin: 0 0 1rem 0;
  }
}

.score-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.score-item {
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: #f3f4f6;
    border-color: #d1d5db;
  }
}

.score-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.score-item-name {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.score-item-points {
  font-weight: 600;
  color: #111827;
  background-color: #e5e7eb;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.score-item-reason {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.4;
}

.no-data {
  text-align: center;
  color: #6b7280;
  font-style: italic;
  padding: 2rem;
  background-color: #f9fafb;
  border-radius: 0.5rem;
  border: 1px dashed #d1d5db;
}

.debug-info {
  background-color: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-top: 1rem;
  
  p {
    margin: 0 0 0.5rem 0;
    font-weight: 500;
    color: #92400e;
  }
  
  pre {
    background: white;
    padding: 0.75rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    overflow-x: auto;
    margin: 0;
    color: #374151;
  }
}
</style>
