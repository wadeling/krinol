import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

export const useResumeStore = defineStore('resume', () => {
  // 状态
  const resumes = ref([])
  const currentResume = ref(null)
  const loading = ref(false)
  const pagination = ref({
    page: 1,
    pageSize: 10,
    total: 0,
    totalPages: 0,
    hasNext: false,
    hasPrev: false
  })

  // 动作
  const fetchResumes = async (page = 1, pageSize = 10) => {
    try {
      console.log('resumeStore.fetchResumes called with page:', page, 'pageSize:', pageSize, 'types:', typeof page, typeof pageSize)
      loading.value = true
      console.log('Making API request with params:', { page, page_size: pageSize })
      const response = await api.get('/resumes/', {
        params: { page, page_size: pageSize }
      })
      
      // 更新简历数据
      resumes.value = response.data.items
      
      // 更新分页信息
      pagination.value = {
        page: response.data.page,
        pageSize: response.data.page_size,
        total: response.data.total,
        totalPages: response.data.total_pages,
        hasNext: response.data.has_next,
        hasPrev: response.data.has_prev
      }
    } catch (error) {
      ElMessage.error('获取简历列表失败')
      console.error('获取简历列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  const uploadResume = async (file) => {
    try {
      loading.value = true
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await api.post('/resumes/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      ElMessage.success('简历上传成功')
      await fetchResumes() // 重新获取简历列表
      return response.data
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '简历上传失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const getResume = async (resumeId) => {
    try {
      loading.value = true
      const response = await api.get(`/resumes/${resumeId}`)
      currentResume.value = response.data
      return response.data
    } catch (error) {
      ElMessage.error('获取简历详情失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteResume = async (resumeId) => {
    try {
      loading.value = true
      await api.delete(`/resumes/${resumeId}`)
      ElMessage.success('简历删除成功')
      await fetchResumes() // 重新获取简历列表
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '简历删除失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    resumes,
    currentResume,
    loading,
    pagination,
    fetchResumes,
    uploadResume,
    getResume,
    deleteResume
  }
})
