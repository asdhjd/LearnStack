<template>
  <div class="tab-panel">
    <div class="content-layout">
      <!-- 左侧：个人信息表单 -->
      <div class="left-section">
        <div class="info-card">
          <h2 class="card-title">基本信息</h2>
          <form class="info-form" @submit.prevent="updateInfo">
            <!-- 头像上传区域 -->
            <div class="form-item avatar-item">
              <label class="label">头像：</label>
              <div class="avatar-wrapper">
                <img
                  :src="avatarUrl"
                  class="avatar-preview"
                  alt="当前头像"
                />
                <input 
                  type="file" 
                  id="avatarInput" 
                  @change="handleAvatar" 
                  accept="image/*" 
                  style="display: none;"
                >
                <button type="button" @click="handleUploadClick" class="upload-btn">上传头像</button>
              </div>
            </div>
            <div class="form-item">
              <span class="label">用户名：</span>
              <span class="value">{{ user.username }}</span>
            </div>
            <div class="form-item">
              <label class="label">昵称：</label>
              <input v-model="nickname" class="input" placeholder="请输入昵称" />
            </div>
            <div class="form-item">
              <label class="label">邮箱：</label>
              <input v-model="email" type="email" class="input" placeholder="请输入邮箱" />
            </div>
            <button type="submit" class="save-btn">保存信息</button>
          </form>
        </div>
      </div>

      <!-- 右侧：资源投稿 / 申请 / 举报 -->
      <div class="right-section">
        <div class="info-panel-container">
          <div class="info-tab-nav">
            <button
              v-for="tab in infoTabs"
              :key="tab.key"
              :class="['info-tab-btn', { active: activeInfoTab === tab.key }]"
              @click="activeInfoTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>

          <div class="info-tab-panels">
            <!-- 修改密码 -->
            <div class="password-section info-tab-panel" v-show="activeInfoTab === 'password'">
              <h2 class="section-title">修改密码</h2>
              <form class="password-form" @submit.prevent="changePasswordHandler">
                <div class="form-item">
                  <label class="label">旧密码：</label>
                  <input 
                    v-model="oldPassword" 
                    type="password" 
                    class="input" 
                    placeholder="请输入旧密码" 
                    required
                  />
                </div>
                <div class="form-item">
                  <label class="label">新密码：</label>
                  <input 
                    v-model="newPassword" 
                    type="password" 
                    class="input" 
                    placeholder="请输入新密码（至少6位）" 
                    required
                    minlength="6"
                  />
                </div>
                <div class="form-item">
                  <label class="label">确认密码：</label>
                  <input 
                    v-model="confirmPassword" 
                    type="password" 
                    class="input" 
                    placeholder="请再次输入新密码" 
                    required
                    minlength="6"
                  />
                </div>
                <div v-if="passwordError" class="error-message">
                  {{ passwordError }}
                </div>
                <button type="submit" class="save-btn" :disabled="changingPassword">
                  {{ changingPassword ? '修改中...' : '修改密码' }}
                </button>
              </form>
            </div>

            <!-- 我的资源投稿 -->
            <div class="submissions-section info-tab-panel" v-show="activeInfoTab === 'submissions'">
              <h2 class="section-title">我的资源投稿</h2>
              
              <div v-if="loadingSubmissions" class="loading-container">
                <div class="loading-spinner"></div>
                <p>加载中...</p>
              </div>

              <div v-else-if="submissionsError" class="error-container">
                <p>{{ submissionsError }}</p>
                <button @click="fetchSubmissions" class="retry-btn">重试</button>
              </div>

              <div v-else-if="submissions.length > 0" class="submissions-list">
                <div 
                  v-for="submission in submissions" 
                  :key="submission.id"
                  class="submission-card"
                  :class="`status-${submission.status}`"
                >
                  <div class="submission-header">
                    <div class="submission-title-section">
                      <h3 class="submission-title">{{ submission.title }}</h3>
                      <div class="submission-meta">
                        <span class="submission-type">{{ getResourceTypeLabel(submission.resource_type) }}</span>
                        <span class="submission-time">{{ formatDate(submission.created_at) }}</span>
                      </div>
                    </div>
                    <div class="submission-status">
                      <span class="status-badge" :class="`status-${submission.status}`">
                        {{ getSubmissionStatusLabel(submission.status) }}
                      </span>
                    </div>
                  </div>

                  <div class="submission-description" v-if="submission.description">
                    {{ submission.description }}
                  </div>

                  <div class="submission-details">
                    <div class="submission-url">
                      <i class="fas fa-link"></i>
                      <a :href="submission.url" target="_blank" class="url-link">{{ submission.url }}</a>
                    </div>
                    <div v-if="submission.reviewed_at" class="reviewed-info">
                      <i class="fas fa-gavel"></i>
                      审核时间：{{ formatDate(submission.reviewed_at) }}
                      <span v-if="submission.reviewed_by_username">（{{ submission.reviewed_by_username }}）</span>
                    </div>
                  </div>

                  <div v-if="submission.admin_notes" class="admin-feedback">
                    <div class="feedback-header">
                      <i class="fas fa-user-shield"></i>
                      <strong>管理员反馈：</strong>
                      <span v-if="submission.reviewed_by_username" class="reviewed-by">
                        审核人：{{ submission.reviewed_by_username }}
                      </span>
                    </div>
                    <div class="feedback-content">
                      {{ submission.admin_notes }}
                    </div>
                  </div>

                  <div v-else-if="submission.status === 'pending'" class="pending-notice">
                    <i class="fas fa-clock"></i>
                    <span>投稿已提交，等待管理员审核...</span>
                  </div>
                </div>
              </div>

              <div v-else class="empty-state">
                <div class="empty-icon">📝</div>
                <h3>暂无投稿</h3>
                <p>您还没有投稿过资源</p>
                <button @click="$router.push('/resources/submit')" class="submit-btn">
                  去投稿资源
                </button>
              </div>
            </div>

            <!-- 资源添加申请列表 -->
            <div class="requests-section info-tab-panel" v-show="activeInfoTab === 'requests'">
              <h2 class="section-title">我的资源添加申请</h2>
        
              <div v-if="loadingRequests" class="loading-container">
                <div class="loading-spinner"></div>
                <p>加载中...</p>
              </div>

              <div v-else-if="requestsError" class="error-container">
                <p>{{ requestsError }}</p>
                <button @click="fetchRequests" class="retry-btn">重试</button>
              </div>

              <div v-else-if="requests.length > 0" class="requests-list">
                <div 
                  v-for="request in requests" 
                  :key="request.id"
                  class="request-card"
                  :class="`status-${request.status}`"
                >
                  <div class="request-header">
                    <div class="request-title-section">
                      <h3 class="request-title">{{ request.title }}</h3>
                      <div class="request-meta">
                        <span class="request-type">{{ getResourceTypeLabel(request.resource_type) }}</span>
                        <span class="request-time">{{ formatDate(request.created_at) }}</span>
                      </div>
                    </div>
                    <div class="request-status">
                      <span class="status-badge" :class="`status-${request.status}`">
                        {{ getStatusLabel(request.status) }}
                      </span>
                    </div>
                  </div>

                  <div class="request-description" v-if="request.description">
                    {{ request.description }}
                  </div>

                  <div class="request-details">
                    <div class="request-url">
                      <i class="fas fa-link"></i>
                      <a :href="request.url" target="_blank" class="url-link">{{ request.url }}</a>
                    </div>
                  </div>

                  <div class="request-reason">
                    <strong>申请理由：</strong>
                    <p>{{ request.reason }}</p>
                  </div>

                  <div v-if="request.admin_notes" class="admin-feedback">
                    <div class="feedback-header">
                      <i class="fas fa-user-shield"></i>
                      <strong>管理员反馈：</strong>
                      <span v-if="request.processed_by_username" class="processed-by">
                        处理人：{{ request.processed_by_username }}
                      </span>
                      <span v-if="request.processed_at" class="processed-time">
                        {{ formatDate(request.processed_at) }}
                      </span>
                    </div>
                    <div class="feedback-content">
                      {{ request.admin_notes }}
                    </div>
                  </div>

                  <div v-else-if="request.status === 'processing'" class="processing-notice">
                    <i class="fas fa-spinner fa-spin"></i>
                    <span>管理员正在处理中，请耐心等待...</span>
                  </div>

                  <div v-else-if="request.status === 'pending'" class="pending-notice">
                    <i class="fas fa-clock"></i>
                    <span>申请已提交，等待管理员处理...</span>
                  </div>
                </div>
              </div>

              <div v-else class="empty-state">
                <div class="empty-icon">📝</div>
                <h3>暂无申请</h3>
                <p>您还没有提交过资源添加申请</p>
                <button @click="$router.push('/resources/submit')" class="submit-btn">
                  去投稿资源
                </button>
              </div>
            </div>

            <!-- 我的举报 -->
            <div class="reports-section info-tab-panel" v-show="activeInfoTab === 'reports'">
              <h2 class="section-title">我的举报</h2>
              
              <div v-if="loadingReports" class="loading-container">
                <div class="loading-spinner"></div>
                <p>加载中...</p>
              </div>

              <div v-else-if="reportsError" class="error-container">
                <p>{{ reportsError }}</p>
                <button @click="fetchReports" class="retry-btn">重试</button>
              </div>

              <div v-else-if="reports.length > 0" class="reports-list">
                <div 
                  v-for="report in reports" 
                  :key="report.id"
                  class="report-card"
                  :class="`status-${report.status}`"
                >
                  <div class="report-header">
                    <div class="report-title-section">
                      <h3 class="report-title">{{ formatReportTarget(report) }}</h3>
                      <div class="report-meta">
                        <span class="report-type">{{ formatReportType(report.target_type) }}</span>
                        <span class="report-time">{{ formatDate(report.created_at) }}</span>
                      </div>
                    </div>
                    <div class="report-status">
                      <span class="status-badge" :class="`status-${report.status}`">
                        {{ formatReportStatus(report.status) }}
                      </span>
                    </div>
                  </div>

                  <div class="report-details">
                    <div class="report-reason">
                      <strong>举报原因：</strong>
                      <span>{{ report.reason }}</span>
                    </div>
                    <div v-if="report.description" class="report-description">
                      <strong>补充说明：</strong>
                      <p>{{ report.description }}</p>
                    </div>
                  </div>

                  <div v-if="report.processed_at" class="processed-info">
                    <i class="fas fa-gavel"></i>
                    处理时间：{{ formatDate(report.processed_at) }}
                    <span v-if="report.processed_by_info">（{{ report.processed_by_info.nickname }}）</span>
                  </div>

                  <div v-if="report.resolution_notes" class="admin-feedback">
                    <div class="feedback-header">
                      <i class="fas fa-user-shield"></i>
                      <strong>处理结果：</strong>
                    </div>
                    <div class="feedback-content">
                      {{ report.resolution_notes }}
                    </div>
                  </div>

                  <div v-else-if="report.status === 'pending'" class="pending-notice">
                    <i class="fas fa-clock"></i>
                    <span>举报已提交，等待管理员处理...</span>
                  </div>
                </div>
              </div>

              <div v-else class="empty-state">
                <div class="empty-icon">🚩</div>
                <h3>暂无举报记录</h3>
                <p>您还没有提交过任何举报</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, getCurrentInstance } from 'vue';
import { getUserInfo, updateUserInfo, changePassword } from '@/services/userService';
import communityService from '@/services/communityService';
import axios from 'axios';

const { appContext } = getCurrentInstance();
const mediaUrl = appContext.config.globalProperties.mediaUrl;

const user = ref({});
const nickname = ref('');
const email = ref('');
const avatarFile = ref(null);

// 修改密码相关
const oldPassword = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const passwordError = ref('');
const changingPassword = ref(false);

const avatarUrl = computed(() => {
  if (!user.value.avatar) {
    return '/default-avatar.png';
  }
  if (user.value.avatar.startsWith('data:image')) {
    return user.value.avatar;
  }
  if (user.value.avatar.startsWith('http://') || user.value.avatar.startsWith('https://')) {
    return user.value.avatar;
  }
  return mediaUrl + user.value.avatar;
});

const requests = ref([]);
const loadingRequests = ref(false);
const requestsError = ref(null);

const submissions = ref([]);
const loadingSubmissions = ref(false);
const submissionsError = ref(null);

const reports = ref([]);
const loadingReports = ref(false);
const reportsError = ref(null);

const infoTabs = [
  { key: 'password', label: '修改密码' },
  { key: 'submissions', label: '我的资源投稿' },
  { key: 'requests', label: '我的资源添加申请' },
  { key: 'reports', label: '我的举报' },
];
const activeInfoTab = ref('password');

onMounted(async () => {
  const data = await getUserInfo();
  user.value = data;
  nickname.value = data.nickname;
  email.value = data.email;
  await Promise.all([fetchRequests(), fetchSubmissions(), fetchReports()]);
});

const handleUploadClick = () => {
  const input = document.getElementById('avatarInput');
  input?.click();
};

const handleAvatar = (e) => {
  const file = e.target.files[0];
  if (file) {
    avatarFile.value = file;
    const reader = new FileReader();
    reader.onload = (event) => {
      user.value.avatar = event.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const updateInfo = async () => {
  const formData = new FormData();
  formData.append('nickname', nickname.value.trim());
  formData.append('email', email.value.trim());
  if (avatarFile.value) {
    formData.append('avatar', avatarFile.value);
  }

  try {
    const updatedUser = await updateUserInfo(formData);
    user.value = updatedUser;
    alert('保存成功！');
  } catch (error) {
    alert('保存失败：' + error.message);
  }
};

const changePasswordHandler = async () => {
  // 重置错误信息
  passwordError.value = '';
  
  // 验证新密码长度
  if (newPassword.value.length < 6) {
    passwordError.value = '新密码长度至少为6位';
    return;
  }
  
  // 验证两次输入的新密码是否一致
  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = '两次输入的新密码不一致';
    return;
  }
  
  // 验证新密码和旧密码是否相同
  if (oldPassword.value === newPassword.value) {
    passwordError.value = '新密码不能与旧密码相同';
    return;
  }
  
  changingPassword.value = true;
  
  try {
    await changePassword(oldPassword.value, newPassword.value);
    alert('密码修改成功！');
    // 清空表单
    oldPassword.value = '';
    newPassword.value = '';
    confirmPassword.value = '';
    passwordError.value = '';
  } catch (error) {
    const errorMessage = error.response?.data?.error || error.message || '密码修改失败';
    passwordError.value = errorMessage;
  } finally {
    changingPassword.value = false;
  }
};

const fetchRequests = async () => {
  loadingRequests.value = true;
  requestsError.value = null;
  
  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.get(
      'http://localhost:8000/api/resources/requests/',
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    requests.value = response.data;
  } catch (error) {
    console.error('获取申请列表失败:', error);
    requestsError.value = error.response?.data?.detail || error.message || '加载失败';
  } finally {
    loadingRequests.value = false;
  }
};

const getStatusLabel = (status) => {
  const labels = {
    'pending': '待处理',
    'processing': '处理中',
    'completed': '已完成',
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

const fetchSubmissions = async () => {
  loadingSubmissions.value = true;
  submissionsError.value = null;
  
  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.get(
      'http://localhost:8000/api/resources/moderation/',
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    submissions.value = response.data;
  } catch (error) {
    console.error('获取投稿列表失败:', error);
    submissionsError.value = error.response?.data?.detail || error.message || '加载失败';
  } finally {
    loadingSubmissions.value = false;
  }
};

const getSubmissionStatusLabel = (status) => {
  const labels = {
    'pending': '待审核',
    'approved': '已通过',
    'rejected': '已拒绝'
  };
  return labels[status] || status;
};

// 获取用户举报记录
const fetchReports = async () => {
  loadingReports.value = true;
  reportsError.value = null;
  
  try {
    const reportsData = await communityService.getReports();
    reports.value = Array.isArray(reportsData) ? reportsData : reportsData.results || [];
  } catch (error) {
    console.error('获取举报记录失败:', error);
    reportsError.value = error.response?.data?.detail || error.message || '加载失败';
  } finally {
    loadingReports.value = false;
  }
};

// 格式化举报类型
const formatReportType = (type) => {
  return type === 'answer' ? '评论' : '帖子';
};

// 格式化举报状态
const formatReportStatus = (status) => {
  const labels = {
    'pending': '待处理',
    'resolved': '已处理',
    'dismissed': '已驳回'
  };
  return labels[status] || status;
};

// 格式化举报目标
const formatReportTarget = (report) => {
  if (report.target_type === 'answer') {
    return `评论：${report.answer_excerpt ? (report.answer_excerpt.length > 60 ? report.answer_excerpt.substring(0, 60) + '...' : report.answer_excerpt) : '[该评论已被删除]'}`;
  }
  return `帖子：${report.question_title || '[该帖子已被删除]'}`;
};
</script>

<style scoped>
.tab-panel {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.content-layout {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 32px;
  align-items: start;
}

.left-section {
  position: sticky;
  top: 85px;
}

.info-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 20px 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.card-title {
  font-size: 1.3rem;
  color: #111827;
  padding-bottom: 16px;
  border-bottom: 2px solid #e5e7eb;
  font-weight: 600;
}

.right-section {
  display: flex;
  flex-direction: column;
}

.info-panel-container {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.info-tab-nav {
  display: flex;
  gap: 12px;
  padding-bottom: 12px;
  margin-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.info-tab-btn {
  padding: 10px 18px;
  border: none;
  background: transparent;
  border-radius: 999px;
  font-size: 0.95rem;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.info-tab-btn.active {
  background: #2563eb;
  color: #fff;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.info-tab-btn:not(.active):hover {
  background: #f3f4f6;
  color: #111827;
}

.info-tab-panels {
  position: relative;
}

.info-tab-panel {
  animation: fadeIn 0.2s ease;
}

.info-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.form-item.avatar-item {
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
}

.avatar-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.label {
  width: 80px;
  color: #6b7280;
  font-weight: 500;
  flex-shrink: 0;
}

.value {
  color: #111827;
  font-weight: 600;
  flex: 1;
}

.input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s;
  background: #ffffff;
}

.input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.upload-btn {
  padding: 10px 20px;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
  color: #374151;
}

.upload-btn:hover {
  background: #e5e7eb;
  border-color: #d1d5db;
}

.avatar-preview {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #e5e7eb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.save-btn {
  margin-top: 8px;
  padding: 14px 28px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  width: 100%;
}

.save-btn:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.save-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

.password-section {
  padding: 20px 0;
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 500px;
}

.password-form .form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-start;
}

.password-form .label {
  width: auto;
  font-weight: 500;
  color: #374151;
}

.password-form .input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s;
  background: #ffffff;
}

.password-form .input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.error-message {
  padding: 12px 16px;
  background: #fee2e2;
  border: 1px solid #fca5a5;
  border-radius: 8px;
  color: #991b1b;
  font-size: 0.9rem;
  margin-top: -8px;
}

.section-title {
  font-size: 1.2rem;
  color: #111827;
  margin-bottom: 16px;
  padding-bottom: 0;
  font-weight: 600;
}

.loading-container, .error-container {
  text-align: center;
  padding: 30px 20px;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #2563eb;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  padding: 8px 16px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 10px;
}

.requests-list,
.submissions-list,
.reports-list {
  display: flex;
  flex-direction: column;
}

.request-card,
.submission-card,
.report-card {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  border-left: 3px solid #e5e7eb;
  transition: all 0.3s;
  margin-bottom: 12px;
}

.request-card:hover,
.submission-card:hover,
.report-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.request-card.status-pending,
.submission-card.status-pending,
.report-card.status-pending {
  border-left-color: #f59e0b;
}

.request-card.status-processing {
  border-left-color: #3b82f6;
}

.request-card.status-completed {
  border-left-color: #10b981;
}

.request-card.status-rejected,
.submission-card.status-rejected,
.report-card.status-dismissed {
  border-left-color: #ef4444;
}

.submission-card.status-approved,
.report-card.status-resolved {
  border-left-color: #10b981;
}

.request-header,
.submission-header,
.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.request-title-section,
.submission-title-section,
.report-title-section {
  flex: 1;
}

.request-title,
.submission-title,
.report-title {
  margin: 0 0 6px 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.4;
}

.request-meta,
.submission-meta,
.report-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 0.8rem;
  color: #6b7280;
}

.request-type,
.submission-type,
.report-type {
  background: #e5e7eb;
  padding: 3px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
}

.request-status,
.submission-status,
.report-status {
  flex-shrink: 0;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
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

.status-badge.status-completed,
.status-badge.status-approved {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.status-rejected,
.status-badge.status-dismissed {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.status-resolved {
  background: #d1fae5;
  color: #065f46;
}

.request-description,
.submission-description,
.report-description {
  color: #666;
  line-height: 1.5;
  margin-bottom: 8px;
  font-size: 0.85rem;
}


.report-description p {
  margin: 4px 0 0 0;
  color: #6b7280;
  line-height: 1.5;
}

.processed-info {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 0.8rem;
  color: #6b7280;
}

.request-details,
.submission-details {
  margin-bottom: 12px;
  font-size: 0.9rem;
  color: #6b7280;
}

.request-url,
.submission-url,
.reviewed-info {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  font-size: 0.8rem;
}

.url-link {
  color: #4285f4;
  text-decoration: none;
  word-break: break-all;
}

.url-link:hover {
  text-decoration: underline;
}

.request-reason,
.report-reason {
  background: #f9fafb;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 8px;
  font-size: 0.85rem;
}

.request-reason strong,
.report-reason strong {
  display: inline;
  color: #374151;
  margin-right: 4px;
}

.request-reason p {
  margin: 4px 0 0 0;
  color: #6b7280;
  line-height: 1.5;
  font-size: 0.85rem;
}

.admin-feedback {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  padding: 10px;
  margin-top: 8px;
}

.feedback-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  font-size: 0.85rem;
}

.feedback-header strong {
  color: #1e40af;
}

.processed-by,
.processed-time,
.reviewed-by {
  color: #6b7280;
  font-size: 0.8rem;
  margin-left: auto;
}

.feedback-content {
  color: #1e3a8a;
  line-height: 1.5;
  font-size: 0.85rem;
  padding-left: 16px;
}

.processing-notice,
.pending-notice {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #fef3c7;
  border-radius: 6px;
  color: #92400e;
  font-size: 0.8rem;
  margin-top: 8px;
}

.processing-notice {
  background: #dbeafe;
  color: #1e40af;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 12px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  color: #374151;
  font-size: 1rem;
}

.empty-state p {
  margin: 0 0 16px 0;
  font-size: 0.9rem;
}

.submit-btn {
  padding: 10px 20px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: background 0.2s;
}

.submit-btn:hover {
  background: #1d4ed8;
}

@media (max-width: 1200px) {
  .content-layout {
    grid-template-columns: 1fr;
  }
  
  .left-section {
    position: static;
  }
  
  .right-section {
    margin-top: 0;
  }
}

@media (max-width: 768px) {
  .info-card,
  .info-panel-container {
    padding: 16px;
  }
  
  .content-layout {
    gap: 16px;
  }
  
  .section-title {
    font-size: 1.1rem;
    margin-bottom: 12px;
  }
}
</style>

