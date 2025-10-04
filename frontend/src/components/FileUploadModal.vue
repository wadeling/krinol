<template>
  <div v-if="isVisible" class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <!-- Modal Header -->
      <div class="modal-header">
        <h3 class="modal-title">上传简历文件</h3>
        <button class="close-btn" @click="closeModal">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <!-- Upload Area -->
        <div 
          class="upload-area"
          :class="{ 'upload-area-dragover': isDragOver, 'upload-area-error': uploadError }"
          @drop="handleDrop"
          @dragover="handleDragOver"
          @dragleave="handleDragLeave"
          @click="triggerFileInput"
        >
          <input
            ref="fileInput"
            type="file"
            accept=".pdf"
            multiple
            @change="handleFileSelect"
            class="hidden"
          />
          
          <div class="upload-content">
            <div class="upload-icon">
              <svg class="w-12 h-12 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
            </div>
            <div class="upload-text">
              <p class="upload-primary">点击或拖拽上传PDF文件</p>
              <p class="upload-secondary">支持多文件上传，.pdf 格式，每个文件最大 10MB</p>
            </div>
          </div>
        </div>

        <!-- Selected Files -->
        <div v-if="selectedFiles.length > 0" class="selected-files">
          <div class="files-header">
            <h4 class="files-title">已选择文件 ({{ selectedFiles.length }})</h4>
            <button class="clear-all-btn" @click="clearAllFiles" v-if="selectedFiles.length > 1">
              清空所有
            </button>
          </div>
          <div class="files-list">
            <div 
              v-for="(file, index) in selectedFiles" 
              :key="index" 
              class="file-item"
            >
              <div class="file-info">
                <div class="file-icon">
                  <svg class="w-6 h-6 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd"></path>
                  </svg>
                </div>
                <div class="file-details">
                  <p class="file-name">{{ file.name }}</p>
                  <p class="file-size">{{ formatFileSize(file.size) }}</p>
                </div>
                <button class="remove-file-btn" @click="removeFile(index)">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="uploadError" class="error-message">
          <svg class="w-2.5 h-2.5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
          </svg>
          <span>{{ uploadError }}</span>
        </div>

        <!-- Upload Progress -->
        <div v-if="isUploading" class="upload-progress">
          <div class="progress-header">
            <h4 class="progress-title">批量上传进度</h4>
            <span class="progress-stats">{{ completedUploads }}/{{ selectedFiles.length }}</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
          </div>
          <p class="progress-text">上传中... {{ uploadProgress }}% ({{ completedUploads }}/{{ selectedFiles.length }})</p>
          
          <!-- Individual file progress -->
          <div v-if="selectedFiles.length > 1" class="file-progress-list">
            <div 
              v-for="(file, index) in selectedFiles" 
              :key="index"
              class="file-progress-item"
            >
              <div class="file-progress-info">
                <span class="file-progress-name">{{ file.name }}</span>
                <span class="file-progress-status" :class="getFileStatusClass(file.status)">
                  {{ getFileStatusText(file.status) }}
                </span>
              </div>
              <div v-if="file.status === 'uploading'" class="file-progress-bar">
                <div class="file-progress-fill" :style="{ width: file.progress + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <button class="btn-cancel" @click="closeModal" :disabled="isUploading">
          取消
        </button>
        <button 
          class="btn-upload" 
          @click="uploadFiles" 
          :disabled="selectedFiles.length === 0 || isUploading"
        >
          <svg v-if="isUploading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{{ getUploadButtonText() }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['update:visible', 'upload-success'])

// Store
const userStore = useUserStore()

// Refs
const fileInput = ref(null)
const selectedFiles = ref([])
const isDragOver = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadError = ref('')
const completedUploads = ref(0)

// Computed
const isVisible = computed(() => props.visible)

// Methods
const closeModal = () => {
  if (!isUploading.value) {
    emit('update:visible', false)
    resetForm()
  }
}

const resetForm = () => {
  selectedFiles.value = []
  isDragOver.value = false
  isUploading.value = false
  uploadProgress.value = 0
  uploadError.value = ''
  completedUploads.value = 0
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  if (files.length > 0) {
    validateAndSetFiles(files)
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  isDragOver.value = false
  
  const files = Array.from(event.dataTransfer.files)
  if (files.length > 0) {
    validateAndSetFiles(files)
  }
}

const handleDragOver = (event) => {
  event.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (event) => {
  event.preventDefault()
  isDragOver.value = false
}

const validateAndSetFiles = (files) => {
  uploadError.value = ''
  const validFiles = []
  
  for (const file of files) {
    // 检查文件类型
    if (file.type !== 'application/pdf') {
      uploadError.value = `文件 ${file.name} 不是 PDF 格式，已跳过`
      continue
    }
    
    // 检查文件大小 (10MB)
    const maxSize = 10 * 1024 * 1024
    if (file.size > maxSize) {
      uploadError.value = `文件 ${file.name} 超过 10MB 限制，已跳过`
      continue
    }
    
    // 添加状态信息
    const fileWithStatus = {
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: file.lastModified,
      status: 'pending',
      progress: 0,
      // 保持原始文件对象的引用，用于上传
      _file: file
    }
    validFiles.push(fileWithStatus)
  }
  
  if (validFiles.length > 0) {
    selectedFiles.value = [...selectedFiles.value, ...validFiles]
  }
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
  uploadError.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const clearAllFiles = () => {
  selectedFiles.value = []
  uploadError.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const uploadFiles = async () => {
  if (selectedFiles.value.length === 0) return
  
  isUploading.value = true
  uploadProgress.value = 0
  uploadError.value = ''
  completedUploads.value = 0
  
  try {
    await uploadMultipleFiles()
    
    // 延迟一下让用户看到结果
    setTimeout(() => {
      closeModal()
    }, 1000)
    
  } catch (error) {
    console.error('Upload error:', error)
    uploadError.value = '上传失败，请重试'
  } finally {
    isUploading.value = false
  }
}

const uploadMultipleFiles = async () => {
  const formData = new FormData()
  
  // 添加所有文件到 FormData
  selectedFiles.value.forEach(file => {
    formData.append('files', file._file)
  })
  
  // 更新所有文件状态为上传中
  selectedFiles.value.forEach(file => {
    file.status = 'uploading'
    file.progress = 0
  })
  
  try {
    const response = await api.post('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${userStore.token}`
      },
      onUploadProgress: (progressEvent) => {
        // 更新总体进度
        uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        
        // 平均分配给所有文件
        const fileProgress = Math.round(uploadProgress.value / selectedFiles.value.length)
        selectedFiles.value.forEach(file => {
          if (file.status === 'uploading') {
            file.progress = fileProgress
          }
        })
      }
    })
    
    // 处理上传结果
    const results = response.data
    let successful = 0
    let failed = 0
    
    // 更新文件状态
    results.forEach((result, index) => {
      if (index < selectedFiles.value.length) {
        const file = selectedFiles.value[index]
        if (result.status === 'uploaded') {
          file.status = 'completed'
          file.progress = 100
          successful++
        } else {
          file.status = 'failed'
          file.progress = 0
          failed++
        }
      }
    })
    
    completedUploads.value = successful
    
    // 生成消息
    let message = ''
    if (successful > 0 && failed === 0) {
      message = `成功上传 ${successful} 个文件`
    } else if (successful > 0 && failed > 0) {
      message = `成功上传 ${successful} 个文件，${failed} 个文件失败`
    } else {
      message = `所有 ${selectedFiles.value.length} 个文件上传失败`
    }
    
    emit('upload-success', { 
      message: message,
      successful: successful,
      failed: failed
    })
    
  } catch (error) {
    console.error('Upload error:', error)
    // 将所有文件标记为失败
    selectedFiles.value.forEach(file => {
      file.status = 'failed'
      file.progress = 0
    })
    throw error
  }
}


const getFileStatusClass = (status) => {
  switch (status) {
    case 'completed':
      return 'status-completed'
    case 'failed':
      return 'status-failed'
    case 'uploading':
      return 'status-uploading'
    default:
      return 'status-pending'
  }
}

const getFileStatusText = (status) => {
  switch (status) {
    case 'completed':
      return '已完成'
    case 'failed':
      return '失败'
    case 'uploading':
      return '上传中'
    default:
      return '等待中'
  }
}

const getUploadButtonText = () => {
  if (isUploading.value) {
    return `上传中... (${completedUploads.value}/${selectedFiles.value.length})`
  }
  if (selectedFiles.value.length === 0) {
    return '选择文件'
  }
  if (selectedFiles.value.length === 1) {
    return '上传文件'
  }
  return `上传 ${selectedFiles.value.length} 个文件`
}
</script>

<style lang="scss" scoped>
/* Modal Overlay */
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

/* Modal Container */
.modal-container {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  width: 100%;
  max-width: 32rem;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Modal Header */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 1.5rem 0 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 1rem;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 0.375rem;
  color: #6b7280;
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background-color: #f3f4f6;
    color: #374151;
  }
}

/* Modal Body */
.modal-body {
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
}

/* Upload Area */
.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background-color: #fafafa;
  
  &:hover {
    border-color: #3b82f6;
    background-color: #f8fafc;
  }
  
  &.upload-area-dragover {
    border-color: #3b82f6;
    background-color: #eff6ff;
  }
  
  &.upload-area-error {
    border-color: #ef4444;
    background-color: #fef2f2;
  }
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-icon {
  color: #9ca3af;
}

.upload-text {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.upload-primary {
  font-size: 1rem;
  font-weight: 500;
  color: #374151;
  margin: 0;
}

.upload-secondary {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

/* Selected Files */
.selected-files {
  margin-top: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background-color: #f9fafb;
  overflow: hidden;
}

.files-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background-color: #f3f4f6;
  border-bottom: 1px solid #e5e7eb;
}

.files-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.clear-all-btn {
  font-size: 0.75rem;
  color: #6b7280;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  transition: all 0.2s;
  
  &:hover {
    background-color: #e5e7eb;
    color: #374151;
  }
}

.files-list {
  max-height: 200px;
  overflow-y: auto;
}

.file-item {
  border-bottom: 1px solid #e5e7eb;
  
  &:last-child {
    border-bottom: none;
  }
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
}

.file-icon {
  flex-shrink: 0;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
  margin: 0 0 0.25rem 0;
  word-break: break-all;
}

.file-size {
  font-size: 0.75rem;
  color: #6b7280;
  margin: 0;
}

.remove-file-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 0.25rem;
  color: #6b7280;
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background-color: #f3f4f6;
    color: #ef4444;
  }
}

/* Error Message */
.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.375rem;
  color: #dc2626;
  font-size: 0.875rem;
}

/* Upload Progress */
.upload-progress {
  margin-top: 1rem;
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.progress-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.progress-stats {
  font-size: 0.75rem;
  color: #6b7280;
  background-color: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.progress-bar {
  width: 100%;
  height: 0.5rem;
  background-color: #e5e7eb;
  border-radius: 0.25rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #3b82f6;
  transition: width 0.3s ease;
}

.progress-text {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
  text-align: center;
}

/* File Progress List */
.file-progress-list {
  margin-top: 1rem;
  max-height: 150px;
  overflow-y: auto;
}

.file-progress-item {
  margin-bottom: 0.75rem;
  padding: 0.5rem;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
}

.file-progress-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.file-progress-name {
  font-size: 0.75rem;
  font-weight: 500;
  color: #374151;
  flex: 1;
  margin-right: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-progress-status {
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 500;
  
  &.status-pending {
    background-color: #f3f4f6;
    color: #6b7280;
  }
  
  &.status-uploading {
    background-color: #dbeafe;
    color: #1e40af;
  }
  
  &.status-completed {
    background-color: #dcfce7;
    color: #166534;
  }
  
  &.status-failed {
    background-color: #fee2e2;
    color: #991b1b;
  }
}

.file-progress-bar {
  width: 100%;
  height: 0.25rem;
  background-color: #e5e7eb;
  border-radius: 0.125rem;
  overflow: hidden;
}

.file-progress-fill {
  height: 100%;
  background-color: #3b82f6;
  transition: width 0.3s ease;
}

/* Modal Footer */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.btn-cancel {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background-color: white;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover:not(:disabled) {
    background-color: #f9fafb;
    border-color: #9ca3af;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn-upload {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  background-color: #3b82f6;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover:not(:disabled) {
    background-color: #2563eb;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

/* Hidden file input */
.hidden {
  display: none;
}

/* Animations */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>

