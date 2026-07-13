<template>
  <div class="admin-dashboard">
    <AdminSidebar />
    
    <div class="admin-content">
      <header class="admin-header">
        <h1>论坛管理</h1>
        <div class="header-actions">
        </div>
      </header>

      <!-- 标签页切换 -->
      <div class="tabs-container">
        <button 
          @click="activeTab = 'questions'" 
          :class="['tab-button', { 'active': activeTab === 'questions' }]"
        >
          <i class="fas fa-comments"></i>
          帖子管理
        </button>
        <button 
          @click="activeTab = 'answers'" 
          :class="['tab-button', { 'active': activeTab === 'answers' }]"
        >
          <i class="fas fa-reply"></i>
          回答管理
        </button>
    <button 
      @click="activeTab = 'reports'" 
      :class="['tab-button', { 'active': activeTab === 'reports' }]"
    >
      <i class="fas fa-flag"></i>
      举报管理
    </button>
      </div>

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
        <button @click="fetchData" class="retry-button">重试</button>
      </div>

      <!-- 帖子管理 -->
      <div v-else-if="activeTab === 'questions'" class="content-section">
        <!-- 搜索和筛选 -->
        <div class="filters-section">
          <div class="search-container">
            <input 
              type="text" 
              v-model="searchQuery" 
              @keyup.enter="handleSearch"
              placeholder="搜索帖子标题、描述或内容..."
              class="search-input"
            />
            <button @click="handleSearch" class="search-btn">
              <i class="fas fa-search"></i>
              搜索
            </button>
          </div>
        </div>

        <!-- 帖子列表 -->
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>标题</th>
                <th>作者</th>
                <th>创建时间</th>
                <th>浏览量</th>
                <th>回答数</th>
                <th>点赞数</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filteredQuestions.length === 0">
                <td colspan="8" class="empty-cell">暂无帖子数据</td>
              </tr>
              <tr v-for="question in filteredQuestions" :key="question.id" class="table-row">
                <td>{{ question.id }}</td>
                <td class="title-cell">
                  <div class="question-title">{{ question.title }}</div>
                  <div class="question-description">{{ truncate(question.description, 50) }}</div>
                </td>
                <td>{{ (question.author_info && question.author_info.nickname) || '匿名用户' }}</td>
                <td>{{ question.created_at }}</td>
                <td>{{ question.views_count }}</td>
                <td>{{ question.answers_count }}</td>
                <td>{{ question.likes_count }}</td>
                <td class="actions-cell">
                  <button @click="viewQuestionDetails(question)" class="action-btn view-btn">
                    <i class="fas fa-eye"></i>
                    查看
                  </button>
                  <button @click="deleteQuestion(question.id)" class="action-btn delete-btn">
                    <i class="fas fa-trash"></i>
                    删除
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- 分页 -->
        <div class="pagination" v-if="!loading && totalQuestions > 0">
          <button 
            class="page-btn" 
            :disabled="questionsPage === 1" 
            @click="questionsPage--"
          >
            上一页
          </button>
          <span class="page-info">
            第 {{ questionsPage }} 页 / 共 {{ questionsTotalPages }} 页 (共 {{ totalQuestions }} 条)
          </span>
          <button 
            class="page-btn" 
            :disabled="questionsPage === questionsTotalPages" 
            @click="questionsPage++"
          >
            下一页
          </button>
        </div>
      </div>

      <!-- 回答管理 -->
      <div v-else-if="activeTab === 'answers'" class="content-section">
        <!-- 搜索和筛选 -->
        <div class="filters-section">
          <div class="search-container">
            <input 
              type="text" 
              v-model="answerSearchQuery" 
              @keyup.enter="handleAnswerSearch"
              placeholder="搜索回答内容..."
              class="search-input"
            />
            <button @click="handleAnswerSearch" class="search-btn">
              <i class="fas fa-search"></i>
              搜索
            </button>
          </div>
        </div>

        <!-- 回答列表 -->
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>帖子标题</th>
                <th>回答内容</th>
                <th>作者</th>
                <th>创建时间</th>
                <th>点赞数</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filteredAnswers.length === 0">
                <td colspan="7" class="empty-cell">暂无回答数据</td>
              </tr>
              <tr v-for="answer in filteredAnswers" :key="answer.id" class="table-row">
                <td>{{ answer.id }}</td>
                <td class="title-cell">{{ getQuestionTitle(answer.question) }}</td>
                <td class="content-cell">{{ truncate(answer.content, 80) }}</td>
                <td>{{ (answer.author_info && answer.author_info.nickname) || '匿名用户' }}</td>
                <td>{{ answer.created_at }}</td>
                <td>{{ answer.likes_count }}</td>
                <td class="actions-cell">
                  <button @click="deleteAnswer(answer.id)" class="action-btn delete-btn">
                    <i class="fas fa-trash"></i>
                    删除
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- 分页 -->
        <div class="pagination" v-if="!loading && totalAnswers > 0">
          <button 
            class="page-btn" 
            :disabled="answersPage === 1" 
            @click="answersPage--"
          >
            上一页
          </button>
          <span class="page-info">
            第 {{ answersPage }} 页 / 共 {{ answersTotalPages }} 页 (共 {{ totalAnswers }} 条)
          </span>
          <button 
            class="page-btn" 
            :disabled="answersPage === answersTotalPages" 
            @click="answersPage++"
          >
            下一页
          </button>
        </div>
      </div>

      <!-- 举报管理 -->
      <div v-else-if="activeTab === 'reports'" class="content-section">
        <div class="filters-section reports-filter">
          <div class="status-filter">
            <label>状态筛选</label>
            <select v-model="reportStatusFilter">
              <option value="pending">待处理</option>
              <option value="resolved">已处理</option>
              <option value="dismissed">已驳回</option>
              <option value="all">全部</option>
            </select>
          </div>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>类型</th>
                <th>对象</th>
                <th>举报人</th>
                <th>原因</th>
                <th>状态</th>
                <th>时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filteredReports.length === 0">
                <td colspan="8" class="empty-cell">暂无举报记录</td>
              </tr>
              <tr v-for="report in filteredReports" :key="report.id">
                <td>{{ report.id }}</td>
                <td>{{ formatReportType(report.target_type) }}</td>
                <td class="title-cell">
                  <div class="question-title">{{ formatReportTarget(report) }}</div>
                  <div class="question-description" v-if="report.description">
                    {{ truncate(report.description, 60) }}
                  </div>
                </td>
                <td>{{ report.reporter_info && report.reporter_info.nickname || '未知用户' }}</td>
                <td>{{ report.reason }}</td>
                <td>
                  <span :class="['status-pill', report.status]">
                    {{ formatReportStatus(report.status) }}
                  </span>
                </td>
                <td>{{ report.created_at }}</td>
                <td class="actions-cell">
                  <button 
                    v-if="report.status === 'pending' && canDeleteContent(report)" 
                    class="action-btn delete-content-btn"
                    @click="handleDeleteReportedContent(report)"
                  >
                    <i class="fas fa-trash"></i>
                    删除内容
                  </button>
                  <span 
                    v-if="report.status === 'pending' && !canDeleteContent(report)" 
                    class="content-deleted-hint"
                  >
                    <i class="fas fa-info-circle"></i>
                    内容已删除
                  </span>
                  <button 
                    v-if="report.status === 'pending'" 
                    class="action-btn dismiss-btn"
                    @click="handleReportAction(report, 'dismissed')"
                  >
                    <i class="fas fa-ban"></i>
                    驳回
                  </button>
                  <span v-else class="resolution-note">
                    {{ report.resolution_notes || '无处理备注' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- 分页 -->
        <div class="pagination" v-if="!loading && totalReports > 0">
          <button 
            class="page-btn" 
            :disabled="reportsPage === 1" 
            @click="reportsPage--"
          >
            上一页
          </button>
          <span class="page-info">
            第 {{ reportsPage }} 页 / 共 {{ reportsTotalPages }} 页 (共 {{ totalReports }} 条)
          </span>
          <button 
            class="page-btn" 
            :disabled="reportsPage === reportsTotalPages" 
            @click="reportsPage++"
          >
            下一页
          </button>
        </div>
      </div>

      <!-- 帖子详情对话框 -->
      <div v-if="showQuestionDialog" class="modal-overlay" @click="closeQuestionDialog">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h2>帖子详情</h2>
            <button @click="closeQuestionDialog" class="close-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body" v-if="selectedQuestion">
            <div class="detail-field">
              <label>标题</label>
              <div class="field-value">{{ selectedQuestion.title }}</div>
            </div>
            <div class="detail-field">
              <label>描述</label>
              <div class="field-value">{{ selectedQuestion.description }}</div>
            </div>
            <div class="detail-field">
              <label>内容</label>
              <div class="field-value content-value">{{ selectedQuestion.content }}</div>
            </div>
            <div class="detail-field">
              <label>标签</label>
              <div class="field-value">{{ selectedQuestion.tags }}</div>
            </div>
            <div class="detail-grid">
              <div class="detail-item">
                <label>作者</label>
                <div>{{ (selectedQuestion.author_info && selectedQuestion.author_info.nickname) || '匿名用户' }}</div>
              </div>
              <div class="detail-item">
                <label>浏览量</label>
                <div>{{ selectedQuestion.views_count }}</div>
              </div>
              <div class="detail-item">
                <label>点赞数</label>
                <div>{{ selectedQuestion.likes_count }}</div>
              </div>
              <div class="detail-item">
                <label>回答数</label>
                <div>{{ selectedQuestion.answers_count }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import AdminSidebar from '@/components/admin/AdminSidebar.vue';
import communityService from '@/services/communityService';
import { ElMessage, ElMessageBox } from 'element-plus';

// Data
const activeTab = ref('questions');
const loading = ref(false);
const error = ref(null);
const questions = ref([]);
const answers = ref([]);
const reports = ref([]);
const searchQuery = ref('');
const answerSearchQuery = ref('');
const reportStatusFilter = ref('all');
const showQuestionDialog = ref(false);
const selectedQuestion = ref(null);

// 分页相关
const pageSize = 10;
const questionsPage = ref(1);
const answersPage = ref(1);
const reportsPage = ref(1);
const totalQuestions = ref(0);
const totalAnswers = ref(0);
const totalReports = ref(0);

// Computed
const filteredQuestions = computed(() => {
  if (!searchQuery.value) return questions.value;
  
  const query = searchQuery.value.toLowerCase();
  return questions.value.filter(q => 
    q.title.toLowerCase().includes(query) ||
    q.description.toLowerCase().includes(query) ||
    (q.content && q.content.toLowerCase().includes(query)) ||
    (q.tags && q.tags.toLowerCase().includes(query))
  );
});

const filteredAnswers = computed(() => {
  if (!answerSearchQuery.value) return answers.value;
  
  const query = answerSearchQuery.value.toLowerCase();
  return answers.value.filter(a => 
    a.content.toLowerCase().includes(query)
  );
});

const filteredReports = computed(() => {
  if (reportStatusFilter.value === 'all') {
    return reports.value;
  }
  return reports.value.filter(report => report.status === reportStatusFilter.value);
});

const pendingReportsCount = computed(() => {
  return reports.value.filter(report => report.status === 'pending').length;
});

const questionsTotalPages = computed(() => Math.ceil(totalQuestions.value / pageSize));
const answersTotalPages = computed(() => Math.ceil(totalAnswers.value / pageSize));
const reportsTotalPages = computed(() => Math.ceil(totalReports.value / pageSize));

// Methods
const fetchQuestions = async () => {
  try {
    loading.value = true;
    error.value = null;
    const response = await communityService.getQuestions({ 
      page: questionsPage.value, 
      page_size: pageSize 
    });
    questions.value = response.results || response;
    if (response.count !== undefined) {
      totalQuestions.value = response.count;
    }
    console.log('获取到的问题列表:', questions.value);
  } catch (err) {
    console.error('获取帖子列表失败:', err);
    error.value = '加载帖子列表失败';
    ElMessage.error('加载帖子列表失败');
  } finally {
    loading.value = false;
  }
};

const fetchAnswers = async () => {
  try {
    loading.value = true;
    error.value = null;
    const response = await communityService.getAllAnswers({ 
      page: answersPage.value, 
      page_size: pageSize 
    });
    answers.value = response.results || response;
    if (response.count !== undefined) {
      totalAnswers.value = response.count;
    }
    console.log('获取到的回答列表:', answers.value);
  } catch (err) {
    console.error('获取回答列表失败:', err);
    error.value = '加载回答列表失败';
    ElMessage.error('加载回答列表失败');
  } finally {
    loading.value = false;
  }
};

const fetchReports = async () => {
  try {
    loading.value = true;
    error.value = null;
    const response = await communityService.getReports({ 
      page: reportsPage.value, 
      page_size: pageSize 
    });
    reports.value = response.results || response;
    if (response.count !== undefined) {
      totalReports.value = response.count;
    }
  } catch (err) {
    console.error('获取举报列表失败:', err);
    error.value = '加载举报列表失败';
    ElMessage.error('加载举报列表失败');
  } finally {
    loading.value = false;
  }
};

const fetchData = async () => {
  await Promise.all([fetchQuestions(), fetchAnswers(), fetchReports()]);
};


const handleSearch = () => {
  // 搜索已通过计算属性处理
};

const handleAnswerSearch = () => {
  // 搜索已通过计算属性处理
};

const viewQuestionDetails = async (question) => {
  try {
    // 获取完整的帖子详情
    const details = await communityService.getQuestionDetail(question.id);
    selectedQuestion.value = details;
    showQuestionDialog.value = true;
  } catch (err) {
    console.error('获取帖子详情失败:', err);
    ElMessage.error('获取帖子详情失败');
  }
};

const closeQuestionDialog = () => {
  showQuestionDialog.value = false;
  selectedQuestion.value = null;
};

const deleteQuestion = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个帖子吗？删除后将无法恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    await communityService.deleteQuestion(id);
    ElMessage.success('删除成功');
    totalQuestions.value--;
    // 如果删除后当前页没有数据且不是第一页，返回上一页
    if (filteredQuestions.value.length === 1 && questionsPage.value > 1) {
      questionsPage.value--;
    } else {
      await fetchQuestions();
    }
  } catch (err) {
    if (err !== 'cancel') {
      console.error('删除帖子失败:', err);
      ElMessage.error('删除帖子失败');
    }
  }
};

const deleteAnswer = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个回答吗？删除后将无法恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    await communityService.deleteAnswer(id);
    ElMessage.success('删除成功');
    totalAnswers.value--;
    // 如果删除后当前页没有数据且不是第一页，返回上一页
    if (filteredAnswers.value.length === 1 && answersPage.value > 1) {
      answersPage.value--;
    } else {
      await fetchAnswers();
    }
  } catch (err) {
    if (err !== 'cancel') {
      console.error('删除回答失败:', err);
      ElMessage.error('删除回答失败');
    }
  }
};

const getQuestionTitle = (questionId) => {
  const question = questions.value.find(q => q.id === questionId);
  return question ? question.title : `帖子 #${questionId}`;
};

const truncate = (text, length) => {
  if (!text) return '';
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
};

const formatReportType = (type) => {
  return type === 'answer' ? '评论' : '帖子';
};

const formatReportStatus = (status) => {
  switch (status) {
    case 'pending':
      return '待处理';
    case 'resolved':
      return '已处理';
    case 'dismissed':
      return '已驳回';
    default:
      return status;
  }
};

const formatReportTarget = (report) => {
  if (report.target_type === 'answer') {
    return `评论：${truncate(report.answer_excerpt || '', 60)}`;
  }
  return `帖子：${report.question_title || '未知标题'}`;
};

const handleReportAction = async (report, nextStatus) => {
  try {
    const actionText = nextStatus === 'resolved' ? '标记为已处理' : '驳回该举报';
    const { value } = await ElMessageBox.prompt(
      '可填写处理备注（可选）',
      actionText,
      {
        confirmButtonText: '提交',
        cancelButtonText: '取消',
        inputPlaceholder: '处理备注（可选）',
        inputValue: ''
      }
    );
    await communityService.updateReport(report.id, {
      status: nextStatus,
      resolution_notes: value || ''
    });
    ElMessage.success('举报状态已更新');
    await fetchReports();
  } catch (err) {
    if (err === 'cancel') return;
    console.error('更新举报状态失败:', err);
    const errorMsg = (err.response && err.response.data && err.response.data.detail) || 
                     (err.response && err.response.data && err.response.data.message) || 
                     (typeof err.response?.data === 'object' ? JSON.stringify(err.response.data) : '') ||
                     err.message || 
                     '更新举报状态失败';
    ElMessage.error(`更新举报状态失败: ${errorMsg}`);
  }
};

const canDeleteContent = (report) => {
  // 检查内容是否还存在（未被删除）
  if (report.target_type === 'question') {
    return report.question !== null && report.question !== undefined;
  } else {
    return report.answer !== null && report.answer !== undefined;
  }
};

const handleDeleteReportedContent = async (report) => {
  try {
    const contentType = report.target_type === 'question' ? '帖子' : '评论';
    const contentId = report.target_type === 'question' ? report.question : report.answer;
    
    if (!contentId) {
      ElMessage.error(`无法获取被举报${contentType}的ID`);
      return;
    }

    await ElMessageBox.confirm(
      `确定要删除这个被举报的${contentType}吗？删除后将无法恢复，并自动标记举报为已处理。`,
      `删除${contentType}`,
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    // 根据举报类型删除对应内容
    if (report.target_type === 'question') {
      // 删除帖子
      await communityService.deleteQuestion(contentId);
    } else {
      // 删除评论
      await communityService.deleteAnswer(contentId);
    }

    // 更新当前举报状态为已处理
    try {
      await communityService.updateReport(report.id, {
        status: 'resolved',
        resolution_notes: `已删除被举报的${contentType}`
      });
    } catch (updateErr) {
      console.warn('更新举报状态失败，但内容已删除:', updateErr);
    }

    // 批量处理同一对象的其他举报
    const relatedReports = reports.value.filter(r => {
      if (r.id === report.id) return false;
      if (r.target_type !== report.target_type) return false;
      if (r.status !== 'pending') return false;
      if (report.target_type === 'question') {
        return r.question === report.question;
      }
      return r.answer === report.answer;
    });

    if (relatedReports.length) {
      try {
        await Promise.all(
          relatedReports.map(r =>
            communityService.updateReport(r.id, {
              status: 'resolved',
              resolution_notes: `已删除被举报的${contentType}`
            })
          )
        );
      } catch (relatedErr) {
        console.warn('批量更新相关举报状态失败:', relatedErr);
      }
    }

    ElMessage.success(`${contentType}已删除，举报已标记为已处理`);
    
    // 刷新数据
    await Promise.all([fetchReports(), fetchQuestions(), fetchAnswers()]);
  } catch (err) {
    if (err === 'cancel') return;
    console.error('删除被举报内容失败:', err);
    const errorMsg = (err.response && err.response.data && err.response.data.detail) || 
                     (err.response && err.response.data && err.response.data.message) || 
                     err.message || 
                     '删除失败';
    ElMessage.error(`删除失败: ${errorMsg}`);
  }
};

onMounted(() => {
  fetchData();
});

// 监听页码变化
watch(() => questionsPage.value, () => {
  fetchQuestions();
});

watch(() => answersPage.value, () => {
  fetchAnswers();
});

watch(() => reportsPage.value, () => {
  fetchReports();
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
  border-bottom: 2px solid #e5e7eb;
}

.admin-header h1 {
  font-size: 28px;
  color: #1f2937;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}



.tabs-container {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e5e7eb;
}

.tab-button {
  padding: 12px 24px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 16px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.tab-button:hover {
  color: #3b82f6;
}

.tab-button.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-spinner {
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.retry-button {
  margin-top: 20px;
  padding: 10px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.content-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filters-section {
  margin-bottom: 20px;
}



.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table thead {
  background: #f9fafb;
  border-bottom: 2px solid #e5e7eb;
}

.data-table th {
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  font-size: 13px;
}

.data-table tr {
  border-bottom: 1px solid #e5e7eb;
}

.data-table td {
  padding: 10px 12px;
  border-bottom: none;
  vertical-align: top;
}

.table-row:hover {
  background: #f9fafb;
}

/* 回答管理和举报管理表格优化 - 更紧凑的间距 */
.content-section .data-table {
  font-size: 13px;
}

.content-section .data-table th {
  padding: 8px 10px;
  font-size: 12px;
}

.content-section .data-table tr {
  border-bottom: 1px solid #e5e7eb;
}

.content-section .data-table td {
  padding: 8px 10px;
  font-size: 12px;
  line-height: 1.4;
  border-bottom: none;
  vertical-align: top;
}

.empty-cell {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}

.title-cell {
  max-width: 280px;
  min-width: 200px;
}

.question-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 3px;
  font-size: 13px;
  line-height: 1.4;
}

.question-description {
  font-size: 11px;
  color: #6b7280;
  line-height: 1.3;
  margin-top: 2px;
}

.content-cell {
  max-width: 350px;
  min-width: 250px;
  word-break: break-word;
  line-height: 1.4;
}

.actions-cell {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: flex-start;
  vertical-align: top;
  height: 100%;
}

.action-btn {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  transition: all 0.2s;
  white-space: nowrap;
}

.view-btn {
  background: #e0f2fe;
  color: #0369a1;
}

.view-btn:hover {
  background: #bae6fd;
}

.delete-btn {
  background: #fee2e2;
  color: #dc2626;
}

.delete-btn:hover {
  background: #fecaca;
}

.delete-content-btn {
  background: #fef2f2;
  color: #991b1b;
}

.delete-content-btn:hover {
  background: #fee2e2;
  border-color: #fca5a5;
}

.dismiss-btn {
  background: #fef3c7;
  color: #92400e;
}

.dismiss-btn:hover {
  background: #fde68a;
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
  border-radius: 8px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
}

.close-btn:hover {
  color: #1f2937;
}

.modal-body {
  padding: 20px;
}

.reports-filter {
  display: flex;
  justify-content: flex-end;
}

.status-filter {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-filter select {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.status-pill.pending {
  background: rgba(245, 158, 11, 0.15);
  color: #b45309;
}

.status-pill.resolved {
  background: rgba(16, 185, 129, 0.2);
  color: #047857;
}

.status-pill.dismissed {
  background: rgba(248, 113, 113, 0.2);
  color: #b91c1c;
}

.resolution-note {
  display: block;
  font-size: 11px;
  color: #6b7280;
  max-width: 200px;
  line-height: 1.3;
  word-break: break-word;
}

.content-deleted-hint {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #9ca3af;
  font-style: italic;
  padding: 4px 8px;
  background: #f3f4f6;
  border-radius: 4px;
}

.detail-field {
  margin-bottom: 20px;
}

.detail-field label {
  display: block;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 8px;
}

.field-value {
  color: #1f2937;
  line-height: 1.6;
}

.content-value {
  white-space: pre-wrap;
  background: #f9fafb;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-top: 20px;
}

.detail-item {
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
}

.detail-item label {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}
  /* 统一搜索样式 */
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
  }

  .search-btn:hover {
    background-color: #2563eb;
  }

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  padding: 20px 0;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #e5e7eb;
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.page-btn:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #6b7280;
  font-size: 14px;
}
</style>