<template>
  <div class="community-forum">
    <div class="forum-container">
      <!-- 左侧边栏 -->
      <aside class="sidebar">
        <div class="sidebar-card stats-card">
          <h3 class="sidebar-title">
            <i class="fas fa-chart-line"></i> 社区统计
          </h3>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ totalQuestions }}</div>
              <div class="stat-label">总帖子</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ totalAnswers }}</div>
              <div class="stat-label">总回答</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ totalViews }}</div>
              <div class="stat-label">总浏览</div>
            </div>
          </div>
        </div>

        <div class="sidebar-card">
          <h3 class="sidebar-title">
            <i class="fas fa-bolt"></i> 最新活动
          </h3>
          <div class="activity-list">
            <div 
              v-for="activity in recentActivities" 
              :key="activity.id"
              class="activity-item"
              @click="navigateToQuestion(activity.id)"
            >
              <div class="activity-header">
                <div class="activity-title">{{ activity.title }}</div>
                <div class="activity-time">{{ formatTime(activity.updated_at || activity.created_at) }}</div>
              </div>
              <div class="activity-stats">
                <span class="activity-stat">
                  <i class="fas fa-comments"></i> {{ activity.answers_count || 0 }}
                </span>
                <span class="activity-stat">
                  <i class="fas fa-eye"></i> {{ activity.views_count || 0 }}
                </span>
              </div>
            </div>
            <p v-if="recentActivities.length === 0" class="no-activity">暂无最新活动</p>
          </div>
        </div>
      </aside>

      <!-- 主内容区 -->
      <main class="main-content">
        <!-- 页面标题和操作栏 -->
        <div class="header-section">
          <div class="page-header">
            <h1>社区问答</h1>
            <p>在这里提问、回答，与其他学习者交流</p>
          </div>

          <!-- 搜索和排序 -->
          <div class="controls-bar">
            <div class="search-wrapper">
              <div class="search-box">
                <i class="fas fa-search search-icon"></i>
                <input 
                  type="text" 
                  v-model="searchQuery" 
                  class="search-input" 
                  placeholder="搜索帖子标题、标签或描述..."
                  @keyup.enter="handleSearch"
                >
                <button 
                  v-if="searchQuery" 
                  class="clear-btn" 
                  @click="clearSearch"
                >
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <button 
                class="search-submit-btn"
                :disabled="!searchQuery.trim()"
                @click="handleSearch"
              >
                <i class="fas fa-search"></i>
                <span>搜索</span>
              </button>
            </div>

            <div class="action-buttons">
              <div class="sort-group">
                <button 
                  :class="['sort-btn', { active: sortBy === 'latest' }]"
                  @click="changeSort('latest')"
                >
                  <i class="fas fa-clock"></i> 最新
                </button>
                <button 
                  :class="['sort-btn', { active: sortBy === 'hot' }]"
                  @click="changeSort('hot')"
                >
                  <i class="fas fa-fire"></i> 热门
                </button>
              </div>
              <div class="right-buttons">
                <button 
                  :class="['filter-btn', { active: showMyQuestions }]"
                  @click="toggleMyQuestions"
                  v-if="isAuthenticated"
                >
                  <i class="fas fa-user"></i> 我的帖子
                </button>
                <router-link to="/community/ask" class="ask-button-primary">
                  <i class="fas fa-plus-circle"></i>
                  <span>发布新帖子</span>
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- 帖子列表 -->
        <div class="posts-container">
          <div v-if="loading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>加载中...</p>
          </div>
          <div v-else-if="error" class="error-state">
            <i class="fas fa-exclamation-circle"></i>
            <p>{{ error }}</p>
            <button @click="fetchQuestions" class="retry-btn">重试</button>
          </div>
          <div v-else-if="questions.length === 0" class="empty-state">
            <i class="fas fa-inbox"></i>
            <h3>暂无帖子</h3>
            <p>成为第一个提问者吧！</p>
            <router-link to="/community/ask" class="primary-btn">
              <i class="fas fa-plus"></i> 立即提问
            </router-link>
          </div>
          <div v-else class="posts-grid">
            <article 
              v-for="question in questions" 
              :key="question.id"
              @click="navigateToQuestion(question.id)"
              :class="['post-card', { 'my-post': isAuthenticated && question.author_info && question.author_info.id === currentUserId }]"
            >
              <div class="post-header">
                <div class="post-author">
                  <div class="author-avatar">
                    <i class="fas fa-user"></i>
                  </div>
                  <div class="author-info">
                    <div class="author-name">{{ (question.author_info && question.author_info.nickname) || '匿名用户' }}</div>
                    <div class="post-time">{{ formatTime(question.created_at) }}</div>
                  </div>
                </div>
                <div v-if="isAuthenticated && question.author_info && question.author_info.id === currentUserId" class="my-badge">
                  <i class="fas fa-check-circle"></i> 我的
                </div>
              </div>

              <div class="post-body">
                <h2 class="post-title">{{ question.title }}</h2>
                <p class="post-excerpt">{{ question.description || '暂无描述' }}</p>
              </div>

              <div class="post-footer">
                <div class="post-stats">
                  <span class="stat-item">
                    <i class="fas fa-eye"></i>
                    <span>{{ question.views_count || 0 }}</span>
                  </span>
                  <span class="stat-item">
                    <i class="fas fa-comments"></i>
                    <span>{{ question.answers_count || 0 }}</span>
                  </span>
                </div>
                <div class="post-tags">
                  <span 
                    v-for="tag in parseTags(question.tags)" 
                    :key="tag"
                    class="tag"
                    @click.stop="searchByTag(tag)"
                  >
                    <i class="fas fa-tag"></i> {{ tag }}
                  </span>
                </div>
              </div>
            </article>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="questions.length > 0 && pagination.total > pagination.per_page" class="pagination-wrapper">
          <div class="pagination">
            <button 
              :disabled="pagination.current_page <= 1"
              @click="changePage(pagination.current_page - 1)"
              class="pagination-btn prev"
            >
              <i class="fas fa-chevron-left"></i>
              <span>上一页</span>
            </button>
            <div class="page-info">
              <span class="current-page">{{ pagination.current_page }}</span>
              <span class="separator">/</span>
              <span class="total-pages">{{ pagination.total_pages }}</span>
            </div>
            <button 
              :disabled="pagination.current_page >= pagination.total_pages"
              @click="changePage(pagination.current_page + 1)"
              class="pagination-btn next"
            >
              <span>下一页</span>
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import communityService from '../services/communityService';

export default {
  name: 'CommunityForum',
  setup() {
    const router = useRouter();
    const questions = ref([]);
    const loading = ref(false);
    const error = ref('');
    const sortBy = ref('latest');
    const searchQuery = ref('');
    const showMyQuestions = ref(false);
    const pagination = ref({
      current_page: 1,
      per_page: 10,
      total: 0,
      total_pages: 1
    });

    // 统计数据
    const totalQuestions = ref(0);
    const totalAnswers = ref(0);
    const totalViews = ref(0);
    const recentActivities = ref([]);

    // 解析标签字符串为数组
    const parseTags = (tagsString) => {
      if (!tagsString) return [];
      return tagsString.split(',').map(tag => tag.trim()).filter(tag => tag);
    };

    // 格式化时间
    const formatTime = (timeString) => {
      if (!timeString) return '';
      const date = new Date(timeString);
      const now = new Date();
      const diff = now - date;
      const minutes = Math.floor(diff / 60000);
      const hours = Math.floor(diff / 3600000);
      const days = Math.floor(diff / 86400000);
      
      if (minutes < 1) return '刚刚';
      if (minutes < 60) return `${minutes}分钟前`;
      if (hours < 24) return `${hours}小时前`;
      if (days < 7) return `${days}天前`;
      
      return date.toLocaleDateString('zh-CN', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    };

    // 按标签搜索
    const searchByTag = (tag) => {
      searchQuery.value = tag;
      pagination.value.current_page = 1;
      fetchQuestions();
    };

    // 获取最新活动（最近有回复或新发布的帖子）
    const fetchRecentActivities = async () => {
      try {
        const response = await communityService.getQuestions({ 
          sort: 'latest',
          page: 1,
          page_size: 5  // 只获取前5个
        });
        const activities = response.results || response;
        // 按更新时间排序，优先显示有回复的帖子
        recentActivities.value = (Array.isArray(activities) ? activities : [])
          .sort((a, b) => {
            // 优先显示有回复的帖子
            if (a.answers_count > 0 && b.answers_count === 0) return -1;
            if (a.answers_count === 0 && b.answers_count > 0) return 1;
            // 然后按更新时间排序
            const timeA = new Date(a.updated_at || a.created_at);
            const timeB = new Date(b.updated_at || b.created_at);
            return timeB - timeA;
          })
          .slice(0, 5);
      } catch (err) {
        console.error('获取最新活动失败:', err);
        recentActivities.value = [];
      }
    };

    // 检查用户是否已登录
    const isAuthenticated = computed(() => {
      return !!localStorage.getItem('access_token');
    });
    
    // 获取当前用户ID
    const currentUserId = computed(() => {
      try {
        // 尝试多种方式获取用户ID
        // 1. 从localStorage的user对象中获取
        const userStr = localStorage.getItem('user');
        if (userStr) {
          try {
            const user = JSON.parse(userStr);
            if (user.id) {
              console.log('从user对象获取用户ID:', user.id);
              return user.id;
            }
          } catch (e) {
            console.warn('解析user对象失败:', e);
          }
        }
        
        // 2. 尝试直接从token中解析（如果token是JWT格式）
        const token = localStorage.getItem('access_token');
        if (token) {
          try {
            const payload = token.split('.')[1];
            if (payload) {
              const decoded = JSON.parse(atob(payload));
              if (decoded.user_id || decoded.sub) {
                const userId = decoded.user_id || decoded.sub;
                console.log('从token获取用户ID:', userId);
                return userId;
              }
            }
          } catch (e) {
            console.warn('从token解析用户ID失败:', e);
          }
        }
        
        console.log('未找到用户ID');
        return null;
      } catch (e) {
        console.error('获取用户ID时发生错误:', e);
        return null;
      }
    });
    
    // 获取帖子列表
    const fetchQuestions = async () => {
      loading.value = true;
      error.value = '';
      try {
        const params = {
          sort: sortBy.value,
          page: pagination.value.current_page
        };
        
        // 如果有搜索关键词，添加到参数中
        if (searchQuery.value.trim()) {
          params.search = searchQuery.value.trim();
        }
        
        // 如果开启了"我发布的"过滤，添加user_id参数
        if (showMyQuestions.value && isAuthenticated.value && currentUserId.value) {
          params.user_id = currentUserId.value;
          console.log('添加用户ID筛选参数:', currentUserId.value);
        }
        
        console.log('发送请求参数:', params);
        
        const response = await communityService.getQuestions(params);
        questions.value = response.results || response;
        if (response.count !== undefined) {
          pagination.value.total = response.count;
          pagination.value.per_page = response.page_size || 10;
          pagination.value.total_pages = Math.ceil(pagination.value.total / pagination.value.per_page);
        }
        
        totalQuestions.value = pagination.value.total;
        totalAnswers.value = response.total_answers || 0;
        totalViews.value = response.total_views || 0;
        
        fetchRecentActivities();
      } catch (err) {
        console.error('获取帖子列表失败:', err);
        error.value = '获取帖子列表失败，请稍后重试';
      } finally {
        loading.value = false;
      }
    };

    // 切换排序方式
    const changeSort = (newSort) => {
      if (sortBy.value !== newSort) {
        sortBy.value = newSort;
        pagination.value.current_page = 1;
        fetchQuestions();
      }
    };
    
    // 处理搜索
    const handleSearch = () => {
      pagination.value.current_page = 1;
      fetchQuestions();
    };
    
    // 清除搜索
    const clearSearch = () => {
      searchQuery.value = '';
      pagination.value.current_page = 1;
      fetchQuestions();
    };
    
    // 切换"我发布的"过滤状态
    const toggleMyQuestions = () => {
      console.log('切换"我发布的"过滤状态，当前登录状态:', isAuthenticated.value);
      console.log('当前用户ID:', currentUserId.value);
      
      if (!isAuthenticated.value) {
        if (confirm('请先登录以查看您发布的帖子')) {
          router.push({
            path: '/login',
            query: { redirect: '/community' }
          });
        }
        return;
      }
      
      if (!currentUserId.value) {
        console.warn('用户已登录但未找到用户ID');
        alert('无法获取用户信息，请重新登录后重试');
        return;
      }
      
      showMyQuestions.value = !showMyQuestions.value;
      console.log('切换后过滤状态:', showMyQuestions.value);
      pagination.value.current_page = 1;
      fetchQuestions();
    };

    // 切换页面
    const changePage = (newPage) => {
      pagination.value.current_page = newPage;
      fetchQuestions();
    };

    // 跳转到帖子详情页
    const navigateToQuestion = (questionId) => {
      router.push(`/community/${questionId}`);
    };

    // 页面加载时获取数据
    onMounted(() => {
      fetchQuestions();
    });

    return {
      questions,
      loading,
      error,
      sortBy,
      searchQuery,
      showMyQuestions,
      isAuthenticated,
      currentUserId,
      pagination,
      totalQuestions,
      totalAnswers,
      totalViews,
      recentActivities,
      parseTags,
      formatTime,
      searchByTag,
      fetchQuestions,
      changeSort,
      changePage,
      navigateToQuestion,
      handleSearch,
      clearSearch,
      toggleMyQuestions
    };
  }
};
</script>

<style scoped>
.community-forum {
  padding: 2rem 0;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: calc(100vh - 120px);
}

.forum-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
  align-items: start;
}

/* 左侧边栏 */
.sidebar {
  position: sticky;
  top: 100px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.sidebar-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.sidebar-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sidebar-title i {
  color: #2563eb;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.stat-item {
  text-align: center;
  padding: 0.5rem;
  background: #f8fafc;
  border-radius: 8px;
  min-width: 0;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2563eb;
  margin-bottom: 0.125rem;
}

.stat-label {
  font-size: 0.75rem;
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.activity-item {
  padding: 0.875rem;
  background: #f8fafc;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.activity-item:hover {
  background: #f1f5f9;
  border-left-color: #2563eb;
  transform: translateX(4px);
}

.activity-header {
  margin-bottom: 0.5rem;
}

.activity-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 0.375rem;
}

.activity-time {
  font-size: 0.75rem;
  color: #94a3b8;
}

.activity-stats {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.activity-stat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #64748b;
}

.activity-stat i {
  font-size: 0.75rem;
  color: #94a3b8;
}

.no-activity {
  color: #94a3b8;
  font-size: 0.9rem;
  text-align: center;
  margin: 1rem 0 0 0;
  padding: 1rem;
}


/* 主内容区 */
.main-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.header-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.page-header {
  margin-bottom: 1.5rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-header p {
  font-size: 1rem;
  color: #64748b;
  margin: 0;
}

.controls-bar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.search-wrapper {
  width: 100%;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.75rem;
  align-items: center;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 1rem;
  color: #94a3b8;
  z-index: 1;
}

.search-input {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 3rem;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s;
  background: #f8fafc;
}

.search-input:focus {
  outline: none;
  border-color: #2563eb;
  background: white;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.clear-btn {
  position: absolute;
  right: 0.75rem;
  padding: 0.5rem;
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  border-radius: 50%;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: #f1f5f9;
  color: #64748b;
}

.search-submit-btn {
  padding: 0.8rem 1.4rem;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
  font-size: 0.95rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.25);
  transition: transform 0.2s, box-shadow 0.2s, opacity 0.2s;
}

.search-submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.3);
}

.search-submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.right-buttons {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-left: auto;
}

.sort-group {
  display: flex;
  gap: 0.5rem;
}

.sort-btn {
  padding: 0.625rem 1.25rem;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
  font-size: 0.95rem;
  font-weight: 500;
  color: #64748b;
}

.sort-btn:hover {
  border-color: #2563eb;
  color: #2563eb;
}

.sort-btn.active {
  background: #2563eb;
  color: white;
  border-color: #2563eb;
}

.filter-btn {
  padding: 0.625rem 1.25rem;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
  font-size: 0.95rem;
  font-weight: 500;
  color: #64748b;
}

.filter-btn:hover {
  border-color: #2563eb;
  color: #2563eb;
}

.filter-btn.active {
  background: #2563eb;
  color: white;
  border-color: #2563eb;
}

.ask-button-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: white;
  border: none;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1rem;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
  transition: all 0.3s;
  white-space: nowrap;
}

.ask-button-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5);
  background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
}

.ask-button-primary i {
  font-size: 1.1rem;
}

.posts-container {
  min-height: 400px;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.loading-state i,
.error-state i,
.empty-state i {
  font-size: 3.5rem;
  color: #cbd5e1;
  margin-bottom: 1rem;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f1f5f9;
  border-top: 4px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1.5rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  color: #ef4444;
}

.retry-btn {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
}

.retry-btn:hover {
  background: #1d4ed8;
  transform: translateY(-2px);
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #1e293b;
  margin: 0.5rem 0;
}

.empty-state p {
  color: #64748b;
  margin-bottom: 1.5rem;
}

.primary-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.75rem;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
}

/* 帖子网格 */
.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.post-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 2px solid transparent;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.post-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #2563eb;
}

.my-post {
  border-color: #2563eb;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.1rem;
}

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.95rem;
}

.post-time {
  font-size: 0.85rem;
  color: #94a3b8;
}

.my-badge {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  background: #2563eb;
  color: white;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.post-body {
  flex: 1;
}

.post-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-excerpt {
  color: #64748b;
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-size: 0.95rem;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.post-stats {
  display: flex;
  gap: 1rem;
}

.post-stats .stat-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  color: #64748b;
  font-size: 0.9rem;
}

.post-stats .stat-item i {
  color: #94a3b8;
}

.post-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  background: #f1f5f9;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #475569;
  transition: all 0.2s;
}

.tag:hover {
  background: #2563eb;
  color: white;
}

.tag i {
  font-size: 0.75rem;
}

.primary-btn {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.3s;
}

.primary-btn:hover {
  background: #2625ebff;
}

.pagination-wrapper {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1.5rem;
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
  color: #64748b;
}

.pagination-btn:hover:not(:disabled) {
  border-color: #2563eb;
  color: #2563eb;
  background: #f8fafc;
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.current-page {
  color: #2563eb;
  font-size: 1.1rem;
}

.separator {
  color: #cbd5e1;
}

.total-pages {
  color: #64748b;
}

@media (max-width: 1024px) {
  .forum-container {
    grid-template-columns: 1fr;
  }
  
  .sidebar {
    position: static;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }
  
  .posts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .forum-container {
    padding: 0 1rem;
    gap: 1rem;
  }
  
  .header-section {
    padding: 1.5rem;
  }
  
  .page-header h1 {
    font-size: 1.75rem;
  }
  
  .controls-bar {
    gap: 0.75rem;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: stretch;
  }
  
  .sort-group {
    width: 100%;
  }
  
  .sort-btn,
  .filter-btn {
    flex: 1;
    justify-content: center;
  }
  
  .post-card {
    padding: 1.25rem;
  }
  
  .post-title {
    font-size: 1.1rem;
  }
  
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
  
  .pagination-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>