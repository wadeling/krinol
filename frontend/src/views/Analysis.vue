<template>
  <div class="analysis">
    <Layout>
      <template #header>
        <div class="header-content">
          <h1>简历分析</h1>
          <p>基于AI的智能简历分析结果</p>
        </div>
      </template>
      
      <template #content>
        <div class="analysis-content">
          <!-- 分析表单 -->
          <el-card class="analysis-form-card" v-if="!currentAnalysis">
            <template #header>
              <h3>开始分析</h3>
            </template>
            
            <el-form
              ref="analysisFormRef"
              :model="analysisForm"
              :rules="analysisRules"
              label-width="100px"
            >
              <el-form-item label="选择简历" prop="resumeId">
                <el-select
                  v-model="analysisForm.resumeId"
                  placeholder="请选择要分析的简历"
                  style="width: 100%"
                  @change="handleResumeChange"
                >
                  <el-option
                    v-for="resume in resumeStore.resumes"
                    :key="resume.id"
                    :label="resume.filename"
                    :value="resume.id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="分析类型" prop="analysisType">
                <el-radio-group v-model="analysisForm.analysisType">
                  <el-radio value="comprehensive">综合分析</el-radio>
                  <el-radio value="skills">技能分析</el-radio>
                  <el-radio value="experience">经验分析</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="职位要求" prop="jobRequirements">
                <el-input
                  v-model="analysisForm.jobRequirements"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入目标职位的要求（可选）"
                />
              </el-form-item>
              
              <el-form-item label="自定义提示" prop="customPrompt">
                <el-input
                  v-model="analysisForm.customPrompt"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入自定义分析要求（可选）"
                />
              </el-form-item>
              
              <el-form-item>
                <el-button
                  type="primary"
                  @click="startAnalysis"
                  :loading="analysisStore.loading"
                >
                  开始分析
                </el-button>
                <el-button @click="resetForm">重置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
          
          <!-- 分析结果 -->
          <el-card class="analysis-result-card" v-if="currentAnalysis">
            <template #header>
              <div class="result-header">
                <h3>分析结果</h3>
                <el-button @click="backToForm">重新分析</el-button>
              </div>
            </template>
            
            <div class="analysis-result">
              <!-- 总体评分 -->
              <div class="score-section">
                <h4>总体评分</h4>
                <div class="score-display">
                  <el-progress
                    :percentage="currentAnalysis.overall_score || 0"
                    :color="getScoreColor(currentAnalysis.overall_score)"
                    :stroke-width="20"
                    text-inside
                  />
                </div>
              </div>
              
              <!-- 优势分析 -->
              <div class="strengths-section">
                <h4>优势分析</h4>
                <el-tag
                  v-for="strength in currentAnalysis.strengths"
                  :key="strength"
                  type="success"
                  class="analysis-tag"
                >
                  {{ strength }}
                </el-tag>
              </div>
              
              <!-- 待改进点 -->
              <div class="weaknesses-section">
                <h4>待改进点</h4>
                <el-tag
                  v-for="weakness in currentAnalysis.weaknesses"
                  :key="weakness"
                  type="warning"
                  class="analysis-tag"
                >
                  {{ weakness }}
                </el-tag>
              </div>
              
              <!-- 改进建议 -->
              <div class="recommendations-section">
                <h4>改进建议</h4>
                <ul class="recommendations-list">
                  <li v-for="recommendation in currentAnalysis.recommendations" :key="recommendation">
                    {{ recommendation }}
                  </li>
                </ul>
              </div>
              
              <!-- 详细分析 -->
              <div class="detailed-analysis">
                <el-tabs v-model="activeTab">
                  <el-tab-pane label="工作经验" name="experience">
                    <div v-if="currentAnalysis.experience_analysis">
                      <p><strong>工作年限：</strong>{{ currentAnalysis.experience_analysis.years_of_experience }}年</p>
                      <p><strong>相关经验：</strong>{{ currentAnalysis.experience_analysis.relevant_experience }}</p>
                      <p><strong>职业发展：</strong>{{ currentAnalysis.experience_analysis.career_progression }}</p>
                    </div>
                  </el-tab-pane>
                  
                  <el-tab-pane label="技能分析" name="skills">
                    <div v-if="currentAnalysis.skills_analysis">
                      <div class="skills-group">
                        <h5>技术技能</h5>
                        <el-tag
                          v-for="skill in currentAnalysis.skills_analysis.technical_skills"
                          :key="skill"
                          class="skill-tag"
                        >
                          {{ skill }}
                        </el-tag>
                      </div>
                      <div class="skills-group">
                        <h5>软技能</h5>
                        <el-tag
                          v-for="skill in currentAnalysis.skills_analysis.soft_skills"
                          :key="skill"
                          type="info"
                          class="skill-tag"
                        >
                          {{ skill }}
                        </el-tag>
                      </div>
                      <div class="skills-group">
                        <h5>技能缺口</h5>
                        <el-tag
                          v-for="gap in currentAnalysis.skills_analysis.skill_gaps"
                          :key="gap"
                          type="danger"
                          class="skill-tag"
                        >
                          {{ gap }}
                        </el-tag>
                      </div>
                    </div>
                  </el-tab-pane>
                  
                  <el-tab-pane label="教育背景" name="education">
                    <div v-if="currentAnalysis.education_analysis">
                      <p><strong>学历水平：</strong>{{ currentAnalysis.education_analysis.education_level }}</p>
                      <p><strong>相关教育：</strong>{{ currentAnalysis.education_analysis.relevant_education }}</p>
                      <div class="certifications">
                        <strong>证书资质：</strong>
                        <el-tag
                          v-for="cert in currentAnalysis.education_analysis.certifications"
                          :key="cert"
                          type="success"
                          class="cert-tag"
                        >
                          {{ cert }}
                        </el-tag>
                      </div>
                    </div>
                  </el-tab-pane>
                </el-tabs>
              </div>
            </div>
          </el-card>
        </div>
      </template>
    </Layout>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import Layout from '@/components/Layout.vue'
import { useResumeStore } from '@/stores/resume'
import { useAnalysisStore } from '@/stores/analysis'

const route = useRoute()
const resumeStore = useResumeStore()
const analysisStore = useAnalysisStore()

const analysisFormRef = ref()
const activeTab = ref('experience')
const currentAnalysis = ref(null)

const analysisForm = reactive({
  resumeId: '',
  analysisType: 'comprehensive',
  jobRequirements: '',
  customPrompt: ''
})

const analysisRules = {
  resumeId: [
    { required: true, message: '请选择要分析的简历', trigger: 'change' }
  ],
  analysisType: [
    { required: true, message: '请选择分析类型', trigger: 'change' }
  ]
}

onMounted(async () => {
  await resumeStore.fetchResumes()
  
  // 如果URL中有resumeId参数，自动选择
  if (route.query.resumeId) {
    analysisForm.resumeId = route.query.resumeId
  }
})

const handleResumeChange = (resumeId) => {
  // 可以在这里添加简历选择后的逻辑
}

const startAnalysis = async () => {
  if (!analysisFormRef.value) return
  
  await analysisFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const response = await analysisStore.analyzeResume({
          resume_id: analysisForm.resumeId,
          analysis_type: analysisForm.analysisType,
          custom_prompt: analysisForm.customPrompt || null,
          job_requirements: analysisForm.jobRequirements || null
        })
        
        // 模拟分析结果（实际应该轮询获取结果）
        setTimeout(() => {
          currentAnalysis.value = {
            overall_score: 85,
            strengths: ['具有5年相关工作经验', '掌握多种编程语言', '有团队管理经验'],
            weaknesses: ['缺乏云计算经验', '英语水平有待提高', '项目管理证书不足'],
            recommendations: ['学习AWS或Azure云平台', '参加英语培训课程', '考取PMP项目管理证书'],
            experience_analysis: {
              years_of_experience: 5,
              relevant_experience: '在软件开发领域有丰富经验',
              career_progression: '从初级开发到技术主管'
            },
            skills_analysis: {
              technical_skills: ['Python', 'Java', 'React', 'MySQL'],
              soft_skills: ['团队协作', '问题解决', '沟通能力'],
              skill_gaps: ['云计算', 'DevOps', '微服务架构']
            },
            education_analysis: {
              education_level: '本科',
              relevant_education: '计算机科学与技术专业',
              certifications: ['Oracle认证', 'Scrum Master']
            }
          }
        }, 2000)
        
        ElMessage.success('分析已开始，请稍候...')
      } catch (error) {
        console.error('分析失败:', error)
      }
    }
  })
}

const resetForm = () => {
  analysisForm.resumeId = ''
  analysisForm.analysisType = 'comprehensive'
  analysisForm.jobRequirements = ''
  analysisForm.customPrompt = ''
  currentAnalysis.value = null
}

const backToForm = () => {
  currentAnalysis.value = null
}

const getScoreColor = (score) => {
  if (score >= 80) return '#67C23A'
  if (score >= 60) return '#E6A23C'
  return '#F56C6C'
}
</script>

<style lang="scss" scoped>
.analysis {
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

.analysis-content {
  padding: 20px;
}

.analysis-form-card,
.analysis-result-card {
  margin-bottom: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  h3 {
    margin: 0;
  }
}

.analysis-result {
  .score-section {
    margin-bottom: 30px;
    
    h4 {
      margin-bottom: 15px;
      color: #333;
    }
    
    .score-display {
      max-width: 400px;
    }
  }
  
  .strengths-section,
  .weaknesses-section,
  .recommendations-section {
    margin-bottom: 30px;
    
    h4 {
      margin-bottom: 15px;
      color: #333;
    }
  }
  
  .analysis-tag {
    margin-right: 8px;
    margin-bottom: 8px;
  }
  
  .recommendations-list {
    list-style: none;
    padding: 0;
    
    li {
      padding: 8px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
    }
  }
  
  .detailed-analysis {
    margin-top: 30px;
    
    .skills-group {
      margin-bottom: 20px;
      
      h5 {
        margin-bottom: 10px;
        color: #333;
      }
      
      .skill-tag {
        margin-right: 8px;
        margin-bottom: 8px;
      }
    }
    
    .certifications {
      margin-top: 10px;
      
      .cert-tag {
        margin-right: 8px;
        margin-bottom: 8px;
      }
    }
  }
}
</style>
