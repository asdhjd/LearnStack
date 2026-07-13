<template>
  <div class="admin-dashboard">
    <AdminSidebar />
    
    <div class="admin-content">
      <header class="admin-header">
        <h1>处理资源申请</h1>
        <div class="header-actions">
          <button @click="fetchRequests" class="refresh-btn" :disabled="loading">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
            刷新
          </button>
        </div>
      </header>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <div class="error-icon">⚠️</div>
        <h3>加载失败</h3>
        <p>{{ error }}</p>
        <button @click="fetchRequests" class="retry-button">重试</button>
      </div>

      <!-- 申请列表 -->
      <div v-else class="requests-container">
        <!-- 筛选和搜索 -->
        <div class="filters-section">
          <div class="filter-group">
            <label for="status-filter">状态筛选：</label>
            <select id="status-filter" v-model="statusFilter" @change="filterRequests">
              <option value="">全部</option>
              <option value="pending">待处理</option>
              <option value="processing">处理中</option>
              <option value="completed">已完成</option>
              <option value="rejected">已拒绝</option>
            </select>
          </div>
          <div class="search-section">
            <div class="search-input-group">
              <div class="search-container">
                <input 
                  type="text" 
                  v-model="searchQuery" 
                  @keyup.enter="handleSearch"
                  placeholder="搜索申请标题、描述或URL..."
                  class="search-input"
                />
                <button @click="handleSearch" class="search-btn">
                  <i class="fas fa-search"></i>
                  搜索
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 申请列表 -->
        <div class="requests-list">
          <div v-if="filteredRequests.length === 0" class="empty-state">
            <div class="empty-icon">📝</div>
            <h3>暂无申请</h3>
            <p>{{ statusFilter ? `没有${getStatusLabel(statusFilter)}的申请` : '暂无任何申请' }}</p>
          </div>
          
          <div v-else>
            <div 
              v-for="request in filteredRequests" 
              :key="request.id"
              class="request-card"
              :class="`status-${request.status}`"
            >
              <div class="request-header">
                <div class="request-title-section">
                  <h3 class="request-title">{{ request.title }}</h3>
                  <div class="request-meta">
                    <span class="request-type">{{ getResourceTypeLabel(request.resource_type) }}</span>
                    <span class="request-audience">{{ request.target_audience || '未指定' }}</span>
                    <span class="request-user">申请人：{{ request.requested_by_username }}</span>
                  </div>
                </div>
                <div class="request-status">
                  <span class="status-badge" :class="`status-${request.status}`">
                    {{ getStatusLabel(request.status) }}
                  </span>
                </div>
              </div>

              <div class="request-description">
                {{ request.description || '无描述' }}
              </div>

              <div class="request-details">
                <div class="request-url">
                  <i class="fas fa-link"></i>
                  <a :href="request.url" target="_blank" class="url-link">{{ request.url }}</a>
                </div>
                <div class="request-time">
                  <i class="fas fa-clock"></i>
                  申请时间：{{ formatDate(request.created_at) }}
                </div>
                <div v-if="request.processed_at" class="request-processed-time">
                  <i class="fas fa-check-circle"></i>
                  处理时间：{{ formatDate(request.processed_at) }}
                </div>
                <div v-if="request.processed_by_username" class="request-processed-by">
                  <i class="fas fa-user-shield"></i>
                  处理人：{{ request.processed_by_username }}
                </div>
              </div>

              <div class="request-reason">
                <strong>申请理由：</strong>
                <p>{{ request.reason }}</p>
              </div>

              <div v-if="request.admin_notes" class="request-admin-notes">
                <strong>管理员备注：</strong>
                <p>{{ request.admin_notes }}</p>
              </div>

              <!-- 操作按钮 -->
              <div class="request-actions">
                <button 
                  v-if="request.status === 'pending'"
                  @click="updateStatus(request.id, 'processing')"
                  class="action-btn processing-btn"
                  :disabled="updating"
                >
                  <i class="fas fa-spinner"></i>
                  标记为处理中
                </button>
                <button 
                  v-if="request.status === 'processing'"
                  @click="updateStatus(request.id, 'completed')"
                  class="action-btn complete-btn"
                  :disabled="updating"
                >
                  <i class="fas fa-check"></i>
                  标记为已完成
                </button>
                <button 
                  v-if="request.status !== 'rejected'"
                  @click="showRejectModal(request)"
                  class="action-btn reject-btn"
                  :disabled="updating"
                >
                  <i class="fas fa-times"></i>
                  拒绝
                </button>
                <button 
                  @click="showNotesModal(request)"
                  class="action-btn notes-btn"
                  :disabled="updating"
                >
                  <i class="fas fa-sticky-note"></i>
                  添加备注
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 拒绝申请模态框 -->
    <div v-if="showRejectModalFlag" class="modal-overlay" @click.self="closeRejectModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>拒绝申请</h3>
          <button @click="closeRejectModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>拒绝原因（可选）</label>
            <textarea 
              v-model="rejectReason" 
              placeholder="请输入拒绝原因..."
              rows="4"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeRejectModal" class="cancel-btn">取消</button>
          <button @click="confirmReject" class="confirm-btn" :disabled="updating">
            {{ updating ? '处理中...' : '确认拒绝' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 添加备注模态框 -->
    <div v-if="showNotesModalFlag" class="modal-overlay" @click.self="closeNotesModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>添加管理员备注</h3>
          <button @click="closeNotesModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>备注内容</label>
            <textarea 
              v-model="adminNotes" 
              placeholder="请输入备注内容..."
              rows="4"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeNotesModal" class="cancel-btn">取消</button>
          <button @click="confirmNotes" class="confirm-btn" :disabled="updating">
            {{ updating ? '保存中...' : '保存备注' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '@/config/api'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'

const loading = ref(false)
const error = ref(null)
const requests = ref([])
const statusFilter = ref('')
const searchQuery = ref('')
const updating = ref(false)
const showRejectModalFlag = ref(false)
const showNotesModalFlag = ref(false)
const currentRequest = ref(null)
const rejectReason = ref('')
const adminNotes = ref('')

// 获取申请列表
const fetchRequests = async () => {
  loading.value = true
  error.value = null
  
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(
      `${API_BASE_URL}/resources/admin/requests/`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )
    requests.value = response.data
  } catch (err) {
    console.error('获取申请列表失败:', err)
    error.value = err.response?.data?.detail || err.message || '加载失败'
  } finally {
    loading.value = false
  }
}

// 筛选申请
const filteredRequests = computed(() => {
  let result = requests.value
  
  // 状态筛选
  if (statusFilter.value) {
    result = result.filter(req => req.status === statusFilter.value)
  }
  
  // 搜索筛选
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(req => 
      req.title.toLowerCase().includes(query) ||
      (req.description && req.description.toLowerCase().includes(query)) ||
      req.url.toLowerCase().includes(query)
    )
  }
  
  return result
})

// 更新申请状态
const updateStatus = async (requestId, newStatus) => {
  if (!confirm(`确定要将申请状态更新为"${getStatusLabel(newStatus)}"吗？`)) {
    return
  }
  
  updating.value = true
  try {
    const token = localStorage.getItem('access_token')
    await axios.post(
      `${API_BASE_URL}/resources/admin/requests/${requestId}/status/`,
      { status: newStatus },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    )
    alert('状态更新成功')
    await fetchRequests()
  } catch (err) {
    console.error('更新状态失败:', err)
    alert(`更新失败：${err.response?.data?.error || err.message || '未知错误'}`)
  } finally {
    updating.value = false
  }
}

// 显示拒绝模态框
const showRejectModal = (request) => {
  currentRequest.value = request
  rejectReason.value = ''
  showRejectModalFlag.value = true
}

// 关闭拒绝模态框
const closeRejectModal = () => {
  showRejectModalFlag.value = false
  currentRequest.value = null
  rejectReason.value = ''
}

// 确认拒绝
const confirmReject = async () => {
  if (!currentRequest.value) return
  
  updating.value = true
  try {
    const token = localStorage.getItem('access_token')
    await axios.post(
      `${API_BASE_URL}/resources/admin/requests/${currentRequest.value.id}/status/`,
      { 
        status: 'rejected',
        admin_notes: rejectReason.value || '申请已拒绝'
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    )
    alert('申请已拒绝')
    closeRejectModal()
    await fetchRequests()
  } catch (err) {
    console.error('拒绝申请失败:', err)
    alert(`操作失败：${err.response?.data?.error || err.message || '未知错误'}`)
  } finally {
    updating.value = false
  }
}

// 显示备注模态框
const showNotesModal = (request) => {
  currentRequest.value = request
  adminNotes.value = request.admin_notes || ''
  showNotesModalFlag.value = true
}

// 关闭备注模态框
const closeNotesModal = () => {
  showNotesModalFlag.value = false
  currentRequest.value = null
  adminNotes.value = ''
}

// 确认保存备注
const confirmNotes = async () => {
  if (!currentRequest.value) return
  
  updating.value = true
  try {
    const token = localStorage.getItem('access_token')
    await axios.post(
      `${API_BASE_URL}/resources/admin/requests/${currentRequest.value.id}/status/`,
      { 
        status: currentRequest.value.status,
        admin_notes: adminNotes.value
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    )
    alert('备注已保存')
    closeNotesModal()
    await fetchRequests()
  } catch (err) {
    console.error('保存备注失败:', err)
    alert(`保存失败：${err.response?.data?.error || err.message || '未知错误'}`)
  } finally {
    updating.value = false
  }
}

// 搜索
const handleSearch = () => {
  // 搜索逻辑已在 computed 中实现
}

// 筛选
const filterRequests = () => {
  // 筛选逻辑已在 computed 中实现
}

// 工具函数
const getStatusLabel = (status) => {
  const labels = {
    'pending': '待处理',
    'processing': '处理中',
    'completed': '已完成',
    'rejected': '已拒绝'
  }
  return labels[status] || status
}

const getResourceTypeLabel = (type) => {
  const labels = {
    'book': '书籍',
    'course': '课程',
    'article': '文章',
    'project': '项目',
    'tool': '工具',
    'document': '文档'
  }
  return labels[type] || type
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchRequests()
})
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.admin-content {
  padding: 20px;
  margin-left: 240px;
  min-height: 100vh;
  box-sizing: border-box;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.admin-header h1 {
  margin: 0;
  color: #333;
  font-size: 2rem;
}

.header-actions {
  display: flex;
  gap: 15px;
}

.refresh-btn {
  padding: 10px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: #2563eb;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-container, .error-container {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.retry-button {
  padding: 10px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 20px;
}

.filters-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-group label {
  font-weight: 500;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
}

.search-section {
  flex: 1;
  max-width: 400px;
}

.search-container {
  display: flex;
  gap: 8px;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
}

.search-btn {
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.requests-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.request-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #e5e7eb;
  margin-bottom: 10px
}

.request-card.status-pending {
  border-left-color: #f59e0b;
}

.request-card.status-processing {
  border-left-color: #3b82f6;
}

.request-card.status-completed {
  border-left-color: #10b981;
}

.request-card.status-rejected {
  border-left-color: #ef4444;
}

.request-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.request-title {
  margin: 0 0 10px 0;
  color: #1f2937;
  font-size: 1.25rem;
}

.request-meta {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  font-size: 0.9rem;
  color: #6b7280;
}

.request-type {
  background: #e5e7eb;
  padding: 4px 8px;
  border-radius: 4px;
}

.request-description {
  color: #666;
  line-height: 1.6;
  margin-bottom: 15px;
}

.request-details {
  margin-bottom: 15px;
  font-size: 0.9rem;
  color: #6b7280;
}

.request-details > div {
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.url-link {
  color: #4285f4;
  text-decoration: none;
}

.url-link:hover {
  text-decoration: underline;
}

.request-reason, .request-admin-notes {
  background: #f9fafb;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 15px;
}

.request-reason strong, .request-admin-notes strong {
  display: block;
  margin-bottom: 8px;
  color: #374151;
}

.request-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.processing-btn {
  background: #3b82f6;
  color: white;
}

.processing-btn:hover:not(:disabled) {
  background: #2563eb;
}

.complete-btn {
  background: #10b981;
  color: white;
}

.complete-btn:hover:not(:disabled) {
  background: #059669;
}

.reject-btn {
  background: #ef4444;
  color: white;
}

.reject-btn:hover:not(:disabled) {
  background: #dc2626;
}

.notes-btn {
  background: #6b7280;
  color: white;
}

.notes-btn:hover:not(:disabled) {
  background: #4b5563;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.status-badge.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.status-processing {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.status-completed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.status-rejected {
  background: #fee2e2;
  color: #991b1b;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
}

.close-btn:hover {
  background: #f3f4f6;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
}

.form-group textarea {
  width: 95%;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
  resize: vertical;
  font-family: inherit;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn, .confirm-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
}

.cancel-btn {
  background: #f3f4f6;
  color: #374151;
}

.cancel-btn:hover {
  background: #e5e7eb;
}

.confirm-btn {
  background: #3b82f6;
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  background: #2563eb;
}

.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

