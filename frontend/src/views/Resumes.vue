<template>
  <div class="resumes">
    <Layout>
      <template #header>
        <div class="header-content">
          <h1>简历管理</h1>
          <p>上传和管理您的简历文件</p>
        </div>
      </template>
      
      <template #content>
        <div class="resumes-content">
          <!-- 上传区域 -->
          <el-card class="upload-card">
            <template #header>
              <h3>上传简历</h3>
            </template>
            
            <el-upload
              ref="uploadRef"
              class="upload-dragger"
              drag
              :action="uploadUrl"
              :headers="uploadHeaders"
              :before-upload="beforeUpload"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :file-list="fileList"
              :auto-upload="false"
              accept=".pdf,.docx,.txt"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 PDF、DOCX、TXT 格式，文件大小不超过 10MB
                </div>
              </template>
            </el-upload>
            
            <div class="upload-actions">
              <el-button type="primary" @click="submitUpload" :loading="resumeStore.loading">
                开始上传
              </el-button>
              <el-button @click="clearFiles">清空列表</el-button>
            </div>
          </el-card>
          
          <!-- 简历列表 -->
          <el-card class="resumes-list-card">
            <template #header>
              <div class="list-header">
                <h3>简历列表</h3>
                <el-button type="primary" @click="refreshResumes">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </template>
            
            <el-table
              :data="resumeStore.resumes"
              :loading="resumeStore.loading"
              stripe
              style="width: 100%"
            >
              <el-table-column prop="filename" label="文件名" min-width="200">
                <template #default="{ row }">
                  <div class="file-info">
                    <el-icon class="file-icon">
                      <Document v-if="row.format === 'pdf'" />
                      <Document v-else-if="row.format === 'docx'" />
                      <Document v-else />
                    </el-icon>
                    <span>{{ row.filename }}</span>
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column prop="format" label="格式" width="80">
                <template #default="{ row }">
                  <el-tag :type="getFormatTagType(row.format)">
                    {{ row.format.toUpperCase() }}
                  </el-tag>
                </template>
              </el-table-column>
              
              <el-table-column prop="file_size" label="大小" width="100">
                <template #default="{ row }">
                  {{ formatFileSize(row.file_size) }}
                </template>
              </el-table-column>
              
              <el-table-column prop="upload_time" label="上传时间" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.upload_time) }}
                </template>
              </el-table-column>
              
              <el-table-column label="操作" width="200" fixed="right">
                <template #default="{ row }">
                  <el-button
                    type="primary"
                    size="small"
                    @click="analyzeResume(row)"
                  >
                    分析
                  </el-button>
                  <el-button
                    type="info"
                    size="small"
                    @click="viewResume(row)"
                  >
                    查看
                  </el-button>
                  <el-button
                    type="danger"
                    size="small"
                    @click="deleteResume(row)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </template>
    </Layout>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import Layout from '@/components/Layout.vue'
import { useResumeStore } from '@/stores/resume'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const resumeStore = useResumeStore()
const userStore = useUserStore()

const uploadRef = ref()
const fileList = ref([])

const uploadUrl = computed(() => '/api/resumes/upload')
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${userStore.token}`
}))

onMounted(() => {
  resumeStore.fetchResumes()
})

const beforeUpload = (file) => {
  const isValidType = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'].includes(file.type)
  const isValidSize = file.size / 1024 / 1024 < 10

  if (!isValidType) {
    ElMessage.error('只能上传 PDF、DOCX、TXT 格式的文件!')
    return false
  }
  if (!isValidSize) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  return true
}

const submitUpload = () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }
  uploadRef.value.submit()
}

const clearFiles = () => {
  fileList.value = []
  uploadRef.value.clearFiles()
}

const handleUploadSuccess = (response, file) => {
  ElMessage.success('文件上传成功')
  resumeStore.fetchResumes()
  clearFiles()
}

const handleUploadError = (error) => {
  ElMessage.error('文件上传失败')
  console.error('Upload error:', error)
}

const refreshResumes = () => {
  resumeStore.fetchResumes()
}

const getFormatTagType = (format) => {
  const typeMap = {
    pdf: 'danger',
    docx: 'primary',
    txt: 'info'
  }
  return typeMap[format] || 'info'
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const analyzeResume = (resume) => {
  router.push({
    name: 'Analysis',
    query: { resumeId: resume.id }
  })
}

const viewResume = (resume) => {
  // 这里可以实现简历预览功能
  ElMessage.info('简历预览功能开发中...')
}

const deleteResume = async (resume) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除简历 "${resume.filename}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await resumeStore.deleteResume(resume.id)
  } catch {
    // 用户取消删除
  }
}
</script>

<style lang="scss" scoped>
.resumes {
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

.resumes-content {
  padding: 20px;
}

.upload-card {
  margin-bottom: 20px;
  
  .upload-dragger {
    width: 100%;
  }
  
  .upload-actions {
    margin-top: 20px;
    text-align: center;
    
    .el-button {
      margin: 0 8px;
    }
  }
}

.resumes-list-card {
  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h3 {
      margin: 0;
    }
  }
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .file-icon {
    color: #409EFF;
  }
}
</style>
