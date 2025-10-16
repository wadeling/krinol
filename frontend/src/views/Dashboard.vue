<template>
  <div class="dashboard-container">
    <!-- Top Nav -->
    <header class="header">
      <div class="header-content">
        <div class="header-inner">
          <!-- Brand -->
          <div class="brand">
            <div class="brand-text">Krinol</div>
            <div class="brand-slogan">智能筛选，精准判断</div>
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
                    <td class="table-cell name-cell" :title="getTooltipTitle(candidate.name, 'name')" ref="nameCell">{{ candidate.name || 'N/A' }}</td>
                    <td class="table-cell phone-cell" :title="getTooltipTitle(candidate.phone, 'phone')" ref="phoneCell">{{ candidate.phone || 'N/A' }}</td>
                    <td class="table-cell position-cell" :title="getTooltipTitle(candidate.position, 'position')" ref="positionCell">{{ candidate.position || 'N/A' }}</td>
                    <td class="table-cell company-cell" :title="getTooltipTitle(candidate.school_name, 'company')" ref="companyCell">{{ candidate.school_name || 'N/A' }}</td>
                    <td class="table-cell graduation-year-cell" :title="getTooltipTitle(candidate.graduation_year, 'graduation')" ref="graduationCell">{{ candidate.graduation_year || 'N/A' }}</td>
                    <td class="table-cell location-cell" :title="getTooltipTitle(candidate.school_city, 'location')" ref="locationCell">{{ candidate.school_city || 'N/A' }}</td>
                    <td class="table-cell email-cell" :title="getTooltipTitle(candidate.email, 'email')" ref="emailCell">{{ candidate.email || 'N/A' }}</td>
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
                        <button 
                          class="add-talent-btn" 
                          :class="{ 
                            'has-evaluation': candidate.interview_score !== null && candidate.interview_score !== undefined,
                            [getInterviewScoreClass(candidate.interview_score)]: candidate.interview_score !== null && candidate.interview_score !== undefined
                          }"
                          @click="showInterviewModal(candidate)"
                        >
                          {{ candidate.interview_score !== null && candidate.interview_score !== undefined ? `面试评价(${candidate.interview_score}分)` : '面试评价' }}
                        </button>
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
                  <select id="pageSize" v-model="pageSize" @change="handlePageSizeChange($event.target.value)" class="page-size-select">
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

    <!-- 面试评价弹窗 -->
    <div v-if="showInterviewModalFlag" class="modal-overlay" @click="closeInterviewModal">
      <div class="interview-modal" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">面试评价</h3>
          <button class="modal-close" @click="closeInterviewModal">×</button>
        </div>
        <div class="modal-content">
          <div class="candidate-info">
            <h4>{{ currentInterviewCandidate?.name }}</h4>
            <p class="candidate-position">{{ currentInterviewCandidate?.position }}</p>
          </div>
          
          <form @submit.prevent="submitInterviewEvaluation" class="interview-form">
            <div class="form-group">
              <label for="interview_score" class="form-label">
                面试分数 <span class="required">*</span>
              </label>
              <input
                id="interview_score"
                v-model="interviewForm.interview_score"
                type="number"
                min="0"
                max="100"
                class="form-input"
                placeholder="请输入面试分数（0-100）"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="interviewer" class="form-label">面试官</label>
              <input
                id="interviewer"
                v-model="interviewForm.interviewer"
                type="text"
                class="form-input"
                placeholder="请输入面试官名字"
                maxlength="100"
              />
            </div>
            
            <div class="form-group">
              <label for="interview_comment" class="form-label">面试评价</label>
              <textarea
                id="interview_comment"
                v-model="interviewForm.interview_comment"
                class="form-textarea"
                placeholder="请输入面试评价内容"
                maxlength="10000"
                rows="6"
              ></textarea>
              <div class="char-count">
                {{ interviewForm.interview_comment.length }}/10000
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn-cancel" @click="closeInterviewModal">
                取消
              </button>
              <button type="submit" class="btn-submit" :disabled="isSubmitting">
                {{ isSubmitting ? '提交中...' : '提交评价' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
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

// 面试评价弹窗状态
const showInterviewModalFlag = ref(false)
const currentInterviewCandidate = ref(null)
const interviewForm = ref({
  interview_score: '',
  interview_comment: '',
  interviewer: ''
})
const isSubmitting = ref(false)

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

// 根据面试分数返回对应的样式类
const getInterviewScoreClass = (score) => {
  if (score === null || score === undefined) {
    return ''
  }
  
  if (score >= 90) {
    return 'score-excellent'  // 90-100分：优秀
  } else if (score >= 80) {
    return 'score-good'       // 80-89分：良好
  } else if (score >= 70) {
    return 'score-average'    // 70-79分：中等
  } else if (score >= 60) {
    return 'score-pass'       // 60-69分：及格
  } else {
    return 'score-fail'       // 0-59分：不及格
  }
}

// 检测文本是否被截断
const isTextTruncated = (element) => {
  if (!element) return false
  return element.scrollWidth > element.clientWidth
}

// 获取tooltip标题（只有被截断时才返回内容）
const getTooltipTitle = (content, type) => {
  if (!content || content === 'N/A') return null
  
  // 根据实际列宽度和中文显示特点调整阈值
  // 基于实际列宽度：name(120px), phone(180px), position(150px), company(180px), graduation(80px), location(80px), email(220px)
  // 中文字符在14px字体下约占用14px宽度，英文字符约7px
  const maxLengths = {
    name: 6,        // 姓名列120px，约6个中文字符
    phone: 15,      // 电话列180px，约15个字符
    position: 8,    // 职位列150px，约8个中文字符
    company: 10,    // 学校列180px，约10个中文字符
    graduation: 4,  // 毕业年份列80px，约4个字符
    location: 4,    // 城市列80px，约4个中文字符
    email: 20       // 邮箱列220px，约20个字符
  }
  
  const maxLength = maxLengths[type] || 8
  return content.length > maxLength ? content : null
}


// 获取候选人数据
const fetchCandidates = async (page = 1, size = 10) => {
  try {
    console.log('fetchCandidates called with page:', page, 'size:', size, 'types:', typeof page, typeof size)
    // 确保参数是数字类型
    const pageNum = parseInt(page)
    const sizeNum = parseInt(size)
    console.log('Parsed values - pageNum:', pageNum, 'sizeNum:', sizeNum, 'types:', typeof pageNum, typeof sizeNum)
    
    // 检查是否为有效数字
    if (isNaN(pageNum) || isNaN(sizeNum) || pageNum <= 0 || sizeNum <= 0) {
      console.error('Invalid parameters - page:', page, 'size:', size, 'parsed as pageNum:', pageNum, 'sizeNum:', sizeNum)
      return
    }
    
    console.log('Calling resumeStore.fetchResumes with pageNum:', pageNum, 'sizeNum:', sizeNum)
    await resumeStore.fetchResumes(pageNum, sizeNum)
    
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
      status: getResumeStatus(resume), // 根据简历状态确定候选人状态
      // 面试评价字段
      interview_score: resume.interview_score || null,
      interview_comment: resume.interview_comment || null,
      interview_date: resume.interview_date || null,
      interviewer: resume.interviewer || null
    }))
    
    // 更新分页信息
    currentPage.value = pageNum
    pageSize.value = sizeNum
    totalCandidates.value = parseInt(resumeStore.pagination?.total) || 0
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
  console.log('handlePageChange called with page:', page, 'type:', typeof page)
  const pageNum = parseInt(page)
  const sizeNum = parseInt(pageSize.value)
  console.log('Parsed values - pageNum:', pageNum, 'sizeNum:', sizeNum, 'isNaN:', isNaN(pageNum), isNaN(sizeNum))
  
  // 检查是否为有效数字
  if (isNaN(pageNum) || isNaN(sizeNum) || pageNum <= 0 || sizeNum <= 0) {
    console.error('Invalid parameters - page:', page, 'pageSize.value:', pageSize.value, 'parsed as pageNum:', pageNum, 'sizeNum:', sizeNum)
    return
  }
  
  currentPage.value = pageNum // 确保转换为数字
  fetchCandidates(pageNum, sizeNum) // 确保pageSize也是数字
}

const handlePageSizeChange = (size) => {
  console.log('handlePageSizeChange called with size:', size, 'type:', typeof size)
  const sizeNum = parseInt(size)
  console.log('Parsed size:', sizeNum, 'type:', typeof sizeNum, 'isNaN:', isNaN(sizeNum))
  
  // 检查是否为有效数字
  if (isNaN(sizeNum) || sizeNum <= 0) {
    console.error('Invalid page size:', size, 'parsed as:', sizeNum)
    return
  }
  
  pageSize.value = sizeNum // 确保转换为数字
  currentPage.value = 1 // 重置到第一页
  console.log('Calling fetchCandidates with page: 1, size:', sizeNum)
  fetchCandidates(1, sizeNum) // 确保传递给API的也是数字
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

// 显示面试评价弹窗
const showInterviewModal = (candidate) => {
  console.log('showInterviewModal called with candidate:', candidate)
  currentInterviewCandidate.value = candidate
  
  // 直接显示弹窗，如果有现有评价则填充数据
  if (candidate.interview_score !== null && candidate.interview_score !== undefined) {
    // 已有评价，填充现有数据
    interviewForm.value = {
      interview_score: candidate.interview_score || '',
      interview_comment: candidate.interview_comment || '',
      interviewer: candidate.interviewer || ''
    }
    console.log('showInterviewModalFlag set to true (existing evaluation)')
  } else {
    // 没有评价，清空表单
    interviewForm.value = {
      interview_score: '',
      interview_comment: '',
      interviewer: ''
    }
    console.log('showInterviewModalFlag set to true (new evaluation)')
  }
  
  showInterviewModalFlag.value = true
}

// 关闭面试评价弹窗
const closeInterviewModal = () => {
  showInterviewModalFlag.value = false
  currentInterviewCandidate.value = null
  interviewForm.value = {
    interview_score: '',
    interview_comment: '',
    interviewer: ''
  }
  isSubmitting.value = false
}

// 提交面试评价
const submitInterviewEvaluation = async () => {
  if (!currentInterviewCandidate.value) return
  
  // 验证必填字段
  if (!interviewForm.value.interview_score || interviewForm.value.interview_score < 0 || interviewForm.value.interview_score > 100) {
    alert('请输入有效的面试分数（0-100）')
    return
  }
  
  if (interviewForm.value.interview_comment && interviewForm.value.interview_comment.length > 10000) {
    alert('面试评价内容不能超过10000字符')
    return
  }
  
  isSubmitting.value = true
  
  try {
    const response = await fetch(`/api/resumes/${currentInterviewCandidate.value.id}/interview`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      },
      body: JSON.stringify({
        interview_score: parseInt(interviewForm.value.interview_score),
        interview_comment: interviewForm.value.interview_comment || null,
        interviewer: interviewForm.value.interviewer || null
      })
    })
    
    if (!response.ok) {
      throw new Error('提交失败')
    }
    
    const result = await response.json()
    console.log('面试评价提交成功:', result)
    
    // 更新本地数据
    currentInterviewCandidate.value.interview_score = result.interview_score
    currentInterviewCandidate.value.interview_comment = result.interview_comment
    currentInterviewCandidate.value.interviewer = result.interviewer
    currentInterviewCandidate.value.interview_date = result.interview_date
    
    alert('面试评价提交成功！')
    closeInterviewModal()
    
  } catch (error) {
    console.error('提交面试评价失败:', error)
    alert('提交失败，请重试')
  } finally {
    isSubmitting.value = false
  }
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
    await fetchCandidates(currentPage.value, pageSize.value)
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
    await fetchCandidates(1, 10) // 明确传递初始参数
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
  flex-direction: column;
  align-items: flex-start;
  gap: 0.25rem;
}

.brand-text {
  font-size: 1.5rem;
  font-weight: 900;
  color: #1e293b;
  line-height: 1;
}

.brand-slogan {
  font-size: 0.75rem;
  font-weight: 500;
  color: #64748b;
  line-height: 1;
  letter-spacing: 0.025em;
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
  table-layout: fixed;
  border-collapse: collapse;
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

/* School列表头样式 */
.table-header-cell:nth-child(4) {
  width: 180px;
  min-width: 180px;
  max-width: 180px;
}

/* Graduation Year列表头样式 */
.table-header-cell:nth-child(5) {
  width: 80px;
  min-width: 80px;
  max-width: 80px;
  text-align: center;
}

/* City列表头样式 */
.table-header-cell:nth-child(6) {
  width: 80px;
  min-width: 80px;
  max-width: 80px;
}

/* Email列表头样式 */
.table-header-cell:nth-child(7) {
  width: 220px;
  min-width: 220px;
  max-width: 220px;
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
  padding: 0.375rem 0.5rem;
  vertical-align: middle;
  height: 28px;
  line-height: 1.2;
  position: relative;
}

/* 只有有title属性的单元格才显示pointer光标和tooltip */
.table-cell[title] {
  cursor: pointer;
}

.table-cell[title]:hover {
  position: relative;
}

/* 自定义tooltip样式 - 只对有title属性的单元格生效 */
.table-cell[title]:hover::after {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background-color: #1f2937;
  color: white;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  white-space: nowrap;
  z-index: 1000;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  pointer-events: none;
  max-width: 300px;
  word-wrap: break-word;
  white-space: normal;
  text-align: left;
  margin-bottom: 5px;
}

.name-cell {
  color: #0ea5e9;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 80px;
  max-width: 120px;
}

.phone-cell, .working-time-cell {
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 120px;
  max-width: 180px;
}

.position-cell {
  color: #059669;
  font-weight: 500;
  min-width: 100px;
  max-width: 150px;
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
  min-width: 160px;
  max-width: 220px;
  width: 180px; /* 固定宽度，增加以显示完整学校名称 */
}

/* City列样式 - 足够显示四个汉字 */
.location-cell {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 60px;
  max-width: 80px;
  text-align: left;
  width: 80px; /* 固定宽度，足够显示四个汉字 */
}

/* Graduation Year列样式 - 较窄，年份只需要4位数字 */
.graduation-year-cell {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 70px;
  max-width: 90px;
  width: 80px; /* 固定宽度，稍微增加以与City列保持距离 */
  text-align: center;
}

/* Email列样式 - 适中宽度，确保邮件地址完整显示 */
.email-cell {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 180px;
  max-width: 240px;
  width: 220px; /* 固定宽度，稍微缩小 */
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


/* 响应式表格样式 */
@media (max-width: 1200px) {
  .name-cell {
    min-width: 70px;
    max-width: 100px;
  }
  
  .phone-cell, .working-time-cell {
    min-width: 100px;
    max-width: 150px;
  }
  
  .position-cell {
    min-width: 90px;
    max-width: 130px;
  }
  
  .company-cell {
    min-width: 140px;
    max-width: 200px;
    width: 160px;
  }
  
  .graduation-year-cell {
    min-width: 60px;
    max-width: 80px;
    width: 70px;
  }
  
  .location-cell {
    min-width: 50px;
    max-width: 70px;
    width: 70px;
  }
  
  .email-cell {
    min-width: 160px;
    max-width: 220px;
    width: 200px;
  }
}

@media (max-width: 768px) {
  .table-cell {
    padding: 0.25rem 0.375rem;
    font-size: 0.8rem;
    height: 24px;
  }
  
  .name-cell {
    min-width: 60px;
    max-width: 80px;
  }
  
  .phone-cell, .working-time-cell {
    min-width: 90px;
    max-width: 120px;
  }
  
  .position-cell {
    min-width: 80px;
    max-width: 110px;
  }
  
  .company-cell {
    min-width: 120px;
    max-width: 160px;
    width: 140px;
  }
  
  .graduation-year-cell {
    min-width: 50px;
    max-width: 70px;
    width: 60px;
  }
  
  .location-cell {
    min-width: 45px;
    max-width: 60px;
    width: 60px;
  }
  
  .email-cell {
    min-width: 140px;
    max-width: 180px;
    width: 160px;
  }
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
  
  &.has-evaluation {
    // 默认颜色（90-100分）
    background-color: #dcfce7;
    color: #166534;
    
    &:hover {
      background-color: #bbf7d0;
    }
    
    // 90-100分：优秀（深绿色）
    &.score-excellent {
      background-color: #10b981;
      color: #ffffff;
      
      &:hover {
        background-color: #059669;
      }
    }
    
    // 80-89分：良好（浅绿色）
    &.score-good {
      background-color: #d1fae5;
      color: #065f46;
      
      &:hover {
        background-color: #a7f3d0;
      }
    }
    
    // 70-79分：中等（黄色）
    &.score-average {
      background-color: #f59e0b;
      color: #ffffff;
      
      &:hover {
        background-color: #d97706;
      }
    }
    
    // 60-69分：及格（橙色）
    &.score-pass {
      background-color: #f97316;
      color: #ffffff;
      
      &:hover {
        background-color: #ea580c;
      }
    }
    
    // 0-59分：不及格（红色）
    &.score-fail {
      background-color: #ef4444;
      color: #ffffff;
      
      &:hover {
        background-color: #dc2626;
      }
    }
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

/* 面试评价弹窗样式 */
.interview-modal {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 
    0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-width: 500px;
  width: 100%;
  max-height: 80vh;
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
}

.candidate-position {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0.25rem 0 0 0;
}

.interview-form {
  margin-top: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.required {
  color: #ef4444;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  &::placeholder {
    color: #9ca3af;
  }
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
}

.char-count {
  text-align: right;
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel,
.btn-submit {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-cancel {
  background-color: #f3f4f6;
  color: #374151;
  
  &:hover {
    background-color: #e5e7eb;
  }
}

.btn-submit {
  background-color: #3b82f6;
  color: white;
  
  &:hover:not(:disabled) {
    background-color: #2563eb;
  }
  
  &:disabled {
    background-color: #9ca3af;
    cursor: not-allowed;
  }
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
