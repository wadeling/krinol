import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

export const useAnalysisStore = defineStore('analysis', () => {
  // 状态
  const analyses = ref([])
  const currentAnalysis = ref(null)
  const loading = ref(false)

  // 动作
  const fetchAnalyses = async () => {
    try {
      loading.value = true
      const response = await api.get('/analysis/')
      analyses.value = response.data
    } catch (error) {
      ElMessage.error('获取分析列表失败')
      console.error('获取分析列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  const analyzeResume = async (analysisData) => {
    try {
      loading.value = true
      const response = await api.post('/analysis/analyze', analysisData)
      ElMessage.success('分析任务已开始，请稍后查看结果')
      return response.data
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '开始分析失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const getAnalysisResult = async (analysisId) => {
    try {
      loading.value = true
      const response = await api.get(`/analysis/${analysisId}`)
      currentAnalysis.value = response.data
      return response.data
    } catch (error) {
      ElMessage.error('获取分析结果失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const pollAnalysisResult = async (analysisId, maxAttempts = 30) => {
    let attempts = 0
    const poll = async () => {
      try {
        const result = await getAnalysisResult(analysisId)
        if (result.status === 'completed') {
          return result
        } else if (result.status === 'failed') {
          throw new Error('分析失败')
        } else if (attempts >= maxAttempts) {
          throw new Error('分析超时')
        } else {
          attempts++
          setTimeout(poll, 2000) // 2秒后重试
        }
      } catch (error) {
        throw error
      }
    }
    return poll()
  }

  return {
    analyses,
    currentAnalysis,
    loading,
    fetchAnalyses,
    analyzeResume,
    getAnalysisResult,
    pollAnalysisResult
  }
})
