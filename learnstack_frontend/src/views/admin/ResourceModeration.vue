<template>
  <div class="admin-dashboard">
    <AdminSidebar />
    
    <div class="admin-content">
      <header class="admin-header">
        <h1>资源审核</h1>
        <div class="header-actions">
          <!-- 刷新按钮已移除 -->
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
        <button @click="fetchResources" class="retry-button">重试</button>
      </div>

      <!-- 资源列表 -->
      <div v-else class="resources-container">


        <!-- 筛选和搜索 -->
        <div class="filters-section">
          <div class="filter-group">
            <label for="status-filter">状态筛选：</label>
            <select id="status-filter" v-model="statusFilter" @change="filterResources">
              <option value="">全部</option>
              <option value="pending">待审核</option>
              <option value="approved">已通过</option>
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
                  placeholder="搜索资源标题、描述或分类..."
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

        <!-- 资源列表 -->
        <div class="resources-list">
          <div v-if="filteredResources.length === 0" class="empty-state">
            <div class="empty-icon">📝</div>
            <h3>暂无资源</h3>
            <p>{{ statusFilter ? `没有${getStatusLabel(statusFilter)}的资源` : '暂无任何资源' }}</p>
          </div>
          
          <div v-else>
            <div 
              v-for="resource in filteredResources" 
              :key="resource.id"
              class="resource-card"
              :class="`status-${resource.status}`"
            >
              <div class="resource-header">
                <div class="resource-title-section">
                  <h3 class="resource-title">{{ resource.title }}</h3>
                  <div class="resource-meta">
                    <span class="resource-type">{{ getResourceTypeLabel(resource.resource_type) }}</span>
                    <span class="resource-rating">
                      <i class="fas fa-star"></i>
                      {{ resource.rating }}/5
                    </span>
                    <span class="resource-audience">{{ resource.target_audience }}</span>
                  </div>
                </div>
                <div class="resource-status">
                  <span class="status-badge" :class="`status-${resource.status}`">
                    {{ getStatusLabel(resource.status) }}
                  </span>
                </div>
              </div>

              <div class="resource-description">
                {{ resource.description }}
              </div>

              <div class="resource-details">
                <div class="resource-url">
                  <i class="fas fa-link"></i>
                  <a :href="resource.url" target="_blank" class="url-link">
                    {{ resource.url }}
                  </a>
                </div>
                
                <div class="resource-categories" v-if="resource.categories_display && resource.categories_display.length">
                  <i class="fas fa-tags"></i>
                  <span 
                    v-for="category in resource.categories_display" 
                    :key="category.id"
                    class="category-tag"
                  >
                    <img 
                      v-if="category.icon_image_url"
                      :src="category.icon_image_url" 
                      :alt="category.name"
                      class="category-tag-icon"
                    />
                    <span v-else class="category-tag-placeholder">{{ category.name.charAt(0) }}</span>
                    {{ category.name }}
                  </span>
                </div>
              </div>

              <div class="resource-footer">
                <div class="resource-info">
                  <div class="submitted-info" v-if="resource.submitted_by_username">
                    <i class="fas fa-user"></i>
                    投稿人：{{ resource.submitted_by_username }}
                  </div>
                  <div class="created-info">
                    <i class="fas fa-calendar"></i>
                    投稿时间：{{ formatDate(resource.created_at) }}
                  </div>
                  <div class="reviewed-info" v-if="resource.reviewed_at">
                    <i class="fas fa-gavel"></i>
                    审核时间：{{ formatDate(resource.reviewed_at) }}
                    <span v-if="resource.reviewed_by_username">（{{ resource.reviewed_by_username }}）</span>
                  </div>
                </div>
                
                <div class="resource-actions" v-if="resource.status === 'pending'">
                  <button 
                    @click="showApproveModal(resource)" 
                    class="action-btn approve-btn"
                    :disabled="processing"
                  >
                    <i class="fas fa-check"></i>
                    通过
                  </button>
                  <button 
                    @click="showRejectModal(resource)" 
                    class="action-btn reject-btn"
                    :disabled="processing"
                  >
                    <i class="fas fa-times"></i>
                    拒绝
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 审核通过模态框 -->
    <div v-if="showApproveModalFlag" class="modal-overlay" @click.self="closeApproveModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>审核通过资源</h3>
          <button @click="closeApproveModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>管理员反馈（可选）</label>
            <textarea 
              v-model="approveNotes" 
              placeholder="可以添加一些反馈意见，用户可以在个人中心看到..."
              rows="4"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeApproveModal" class="cancel-btn">取消</button>
          <button @click="confirmApprove" class="confirm-btn" :disabled="processing">
            {{ processing ? '处理中...' : '确认通过' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 拒绝资源模态框 -->
    <div v-if="showRejectModalFlag" class="modal-overlay" @click.self="closeRejectModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>拒绝资源</h3>
          <button @click="closeRejectModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>拒绝原因 <span class="required">*</span></label>
            <textarea 
              v-model="rejectNotes" 
              placeholder="请说明拒绝原因，用户可以在个人中心看到..."
              rows="4"
              required
            ></textarea>
            <p class="form-hint">请详细说明拒绝原因，帮助用户了解问题所在</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeRejectModal" class="cancel-btn">取消</button>
          <button @click="confirmReject" class="confirm-btn" :disabled="processing || !rejectNotes.trim()">
            {{ processing ? '处理中...' : '确认拒绝' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import AdminSidebar from '@/components/admin/AdminSidebar.vue';
import axios from 'axios';
import { API_BASE_URL } from '@/config/api';

// 响应式数据
const resources = ref([]);
const loading = ref(true);
const error = ref('');
const processing = ref(false);
const statusFilter = ref('');
const searchQuery = ref('');
const searchQueryToApply = ref('');

// 模态框相关
const showApproveModalFlag = ref(false);
const showRejectModalFlag = ref(false);
const currentResource = ref(null);
const approveNotes = ref('');
const rejectNotes = ref('');

// 计算属性
const filteredResources = computed(() => {
  let filtered = resources.value;
  
  // 状态筛选
  if (statusFilter.value) {
    filtered = filtered.filter(resource => resource.status === statusFilter.value);
  }
  
  // 搜索筛选
  if (searchQueryToApply.value) {
    const query = searchQueryToApply.value.toLowerCase();
    filtered = filtered.filter(resource => 
      resource.title.toLowerCase().includes(query) ||
      resource.description.toLowerCase().includes(query)
    );
  }
  
  return filtered;
});

const handleSearch = () => {
  searchQueryToApply.value = searchQuery.value;
};



// 方法
const fetchResources = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('未找到登录令牌');
    }
    
    const response = await axios.get(`${API_BASE_URL}/resources/moderation/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    resources.value = response.data;
  } catch (err) {
    console.error('获取资源列表失败:', err);
    error.value = err.response?.data?.error || '获取资源列表失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};



const filterResources = () => {
  // 保持兼容性，确保状态筛选立即生效
  // 搜索筛选通过handleSearch函数触发
};

// 显示审核通过模态框
const showApproveModal = (resource) => {
  console.log('显示审核通过模态框', resource);
  currentResource.value = resource;
  approveNotes.value = '';
  showApproveModalFlag.value = true;
  console.log('showApproveModalFlag:', showApproveModalFlag.value);
};

// 关闭审核通过模态框
const closeApproveModal = () => {
  showApproveModalFlag.value = false;
  currentResource.value = null;
  approveNotes.value = '';
};

// 确认审核通过
const confirmApprove = async () => {
  if (!currentResource.value) return;
  
  processing.value = true;
  
  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.post(
      `${API_BASE_URL}/resources/moderation/${currentResource.value.id}/approve/`,
      {
        admin_notes: approveNotes.value
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (response.data.success) {
      alert('资源审核通过');
      // 更新本地数据
      const resource = resources.value.find(r => r.id === currentResource.value.id);
      if (resource) {
        resource.status = 'approved';
        resource.reviewed_at = new Date().toISOString();
        if (approveNotes.value) {
          resource.admin_notes = approveNotes.value;
        }
      }
      closeApproveModal();
    }
  } catch (err) {
    console.error('审核失败:', err);
    alert('审核失败，请稍后重试');
  } finally {
    processing.value = false;
  }
};

// 显示拒绝模态框
const showRejectModal = (resource) => {
  console.log('显示拒绝模态框', resource);
  currentResource.value = resource;
  rejectNotes.value = '';
  showRejectModalFlag.value = true;
  console.log('showRejectModalFlag:', showRejectModalFlag.value);
};

// 关闭拒绝模态框
const closeRejectModal = () => {
  showRejectModalFlag.value = false;
  currentResource.value = null;
  rejectNotes.value = '';
};

// 确认拒绝
const confirmReject = async () => {
  if (!currentResource.value || !rejectNotes.value.trim()) {
    alert('请填写拒绝原因');
    return;
  }
  
  processing.value = true;
  
  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.post(
      `${API_BASE_URL}/resources/moderation/${currentResource.value.id}/reject/`,
      {
        admin_notes: rejectNotes.value
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (response.data.success) {
      alert('资源已拒绝');
      // 更新本地数据
      const resource = resources.value.find(r => r.id === currentResource.value.id);
      if (resource) {
        resource.status = 'rejected';
        resource.reviewed_at = new Date().toISOString();
        resource.admin_notes = rejectNotes.value;
      }
      closeRejectModal();
    }
  } catch (err) {
    console.error('拒绝失败:', err);
    alert('拒绝失败，请稍后重试');
  } finally {
    processing.value = false;
  }
};

const getStatusLabel = (status) => {
  const labels = {
    'pending': '待审核',
    'approved': '已通过',
    'rejected': '已拒绝'
  };
  return labels[status] || status;
};

const getResourceTypeLabel = (type) => {
  const labels = {
    'book': '书籍',
    'course': '课程',
    'article': '文章',
    'project': '项目',
    'tool': '工具',
    'document': '文档'
  };
  return labels[type] || type;
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

// 初始化
onMounted(() => {
  fetchResources();
  // 初始化搜索查询
  searchQueryToApply.value = searchQuery.value;
});
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



.fa-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 加载和错误状态 */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4285f4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.retry-button {
  padding: 10px 20px;
  background-color: #4285f4;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
  margin-top: 20px;
}

.retry-button:hover {
  background-color: #3367d6;
}



/* 筛选和搜索 */
.filters-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  gap: 20px;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-group label {
  font-weight: 500;
  color: #374151;
}

.filter-group select {
  padding: 11px 16px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  height: 40px;
  box-sizing: border-box;
}

.search-section {
  flex: 1;
}

/* 统一的搜索容器样式 */
.search-input-group {
  display: flex;
  align-items: center;
  gap: 10px; /* 添加按钮间距 */
}

.search-container {
  display: flex;
  align-items: center;
  gap: 0;
}

/* 统一的搜索输入框样式 */
.search-input {
  padding: 11px 16px;
  border: 1px solid #d1d5db;
  border-radius: 4px 0 0 4px;
  width: 300px;
  font-size: 14px;
  border-right: none;
  box-sizing: border-box;
  height: 40px;
}

/* 统一的搜索按钮样式 */
.search-btn {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background-color 0.2s;
  height: 40px;
  box-sizing: border-box;
}

.search-btn:hover {
  background-color: #2563eb;
}

/* 资源列表 */
.resources-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.empty-state p {
  margin: 0;
  color: #666;
}

.resource-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #e5e7eb;
  transition: all 0.2s;
  margin-bottom: 10px;
}

.resource-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.resource-card.status-pending {
  border-left-color: #ff9800;
}

.resource-card.status-approved {
  border-left-color: #4caf50;
}

.resource-card.status-rejected {
  border-left-color: #f44336;
}

.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.resource-title-section {
  flex: 1;
}

.resource-title {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 1.3rem;
}

.resource-meta {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.resource-type,
.resource-rating,
.resource-audience {
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #374151;
}

.resource-rating {
  color: #f59e0b;
}

.resource-status {
  flex-shrink: 0;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.status-badge.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.status-approved {
  background: #d4edda;
  color: #155724;
}

.status-badge.status-rejected {
  background: #f8d7da;
  color: #721c24;
}

.resource-description {
  color: #666;
  line-height: 1.6;
  margin-bottom: 15px;
}

.resource-details {
  margin-bottom: 20px;
}

.resource-url {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.url-link {
  color: #4285f4;
  text-decoration: none;
  word-break: break-all;
}

.url-link:hover {
  text-decoration: underline;
}

.resource-categories {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.category-tag {
  background: #e9ecef;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #495057;
  display: flex;
  align-items: center;
  gap: 4px;
}

.category-tag-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
  border-radius: 3px;
}

.category-tag-placeholder {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
}

.resource-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #e5e7eb;
}

.resource-info {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  font-size: 0.9rem;
  color: #666;
}

.resource-info > div {
  display: flex;
  align-items: center;
  gap: 5px;
}

.resource-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.approve-btn {
  background: #4caf50;
  color: white;
}

.approve-btn:hover:not(:disabled) {
  background: #45a049;
}

.reject-btn {
  background: #f44336;
  color: white;
}

.reject-btn:hover:not(:disabled) {
  background: #da190b;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 模态框样式 */
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
  transition: background-color 0.2s;
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
  width: 100%;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
}

.form-group textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-hint {
  font-size: 0.85rem;
  color: #6b7280;
  margin-top: 4px;
}

.required {
  color: #ef4444;
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
  transition: all 0.2s;
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