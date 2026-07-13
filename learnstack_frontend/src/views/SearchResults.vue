<template>
  <div class="search-results-container">

    <!-- 搜索结果统计 -->
    <div class="search-stats" v-if="searchQuery">
      <p>"{{ searchQuery }}" 的搜索结果: 共 {{ resources.length }} 条</p>
      <p v-if="loading" class="loading-text">搜索中...</p>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- 搜索结果区域 -->
    <div class="results-area">
      <!-- 学习资源结果 -->
      <div class="resources-section">
        <div v-if="loading" class="loading-indicator">
          <div class="spinner"></div>
          正在搜索学习资源...
        </div>
        <div v-else-if="resources.length === 0 && searchQuery" class="no-results">
          没有找到相关学习资源，请尝试其他关键词
        </div>
        <div v-else-if="searchQuery" class="resources-grid">
          <div
            v-for="resource in resources"
            :key="resource.id"
            class="resource-card"
          >
            <!-- 封面图片 -->
            <div v-if="resource.hero_cover" class="resource-cover">
              <img 
                :src="resource.hero_cover" 
                :alt="resource.title"
                :crossorigin="getImageCorsAttribute(resource.hero_cover)"
                :referrerpolicy="getImageReferrerPolicy(resource.hero_cover)"
                @error="handleImageError"
                @load="handleImageLoad"
                class="cover-image"
              />
            </div>
            
            <!-- 内容区域 -->
            <div class="resource-card-content">
              <!-- 资源标题和类型 -->
              <div class="resource-header">
              <h2 v-html="highlightSearchTerm(resource.title)"></h2>
              <div class="resource-type">{{ getResourceTypeLabel(resource.resource_type) }}</div>
            </div>
            
            <!-- 资源评分 -->
            <div class="resource-rating">
              <span class="stars">
                <i v-for="n in 5" :key="n" class="fas fa-star" :class="{ 'filled': n <= (resource.rating || 0) }"></i>
              </span>
              <span class="rating-text">{{ (resource.rating || 0) }}/5</span>
            </div>
            
            <!-- 资源描述 -->
            <p class="resource-description" v-html="highlightSearchTerm((resource.description && resource.description.substring(0, 150)) || '') + (resource.description && resource.description.length > 150 ? '...' : '')"></p>
            
            <!-- 资源元信息 -->
            <div class="resource-meta">
              <!-- 开发者级别 -->
              <span class="developer-level" v-if="resource.target_audience_display || resource.target_audience">
                <i class="fas fa-user"></i> {{ resource.target_audience_display || resource.target_audience }}
              </span>
              
              <!-- 关联分类 -->
              <div class="categories">
                <span v-for="category in (resource.categories_display || [])" :key="category.id" class="category-tag">
                  <img 
                    v-if="category.icon_image_url"
                    :src="category.icon_image_url" 
                    :alt="category.name"
                    class="category-tag-icon"
                  />
                  <span v-else class="category-tag-placeholder">{{ category.name.charAt(0) }}</span>
                  {{ category.name }}
                </span>
                <span v-if="!resource.categories_display || resource.categories_display.length === 0" class="category-tag">
                  <i class="fas fa-folder"></i> {{ resource.category_name || '未分类' }}
                </span>
              </div>
            </div>
            
            <!-- 按钮组：查看资源和收藏 -->
            <div class="resource-actions">
              <!-- 资源链接 -->
              <router-link
                v-if="resource.id"
                :to="{ name: 'ResourceDetail', params: { id: resource.id } }"
                class="resource-link"
                @click.stop
              >
                <i class="fas fa-book-open"></i> 查看资源
              </router-link>
              <a
                v-else
                :href="resource.url"
                target="_blank"
                rel="noopener"
                class="resource-link"
                @click.stop
              >
                <i class="fas fa-external-link-alt"></i> 查看资源
              </a>
              
              <!-- 收藏按钮（仅登录用户可见且未收藏时显示） -->
              <button 
                v-if="isLoggedIn && !isResourceFavorited(resource.id)" 
                @click="handleFavorite(resource)" 
                class="favorite-btn"
                @click.stop
              >
                <i class="fas fa-heart"></i> 收藏
              </button>
            </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 初始状态 -->
    <div v-if="!searchQuery && !loading" class="initial-state">
      <div class="initial-icon">
        <i class="fas fa-search"></i>
      </div>
      <h2>搜索学习资源</h2>
      <p>输入技术关键词，如 "Java 多线程"、"Python 数据分析" 等，快速查找相关学习资源</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios'
import { API_BASE_URL } from '@/config/api';
import { useUserStore } from '@/stores/user';
import { 
  getImageCorsAttribute, 
  getImageReferrerPolicy, 
  handleImageError, 
  handleImageLoad 
} from '@/utils/imageUtils';

// 路由和导航
const route = useRoute();

// 用户状态管理
const userStore = useUserStore();
const currentUser = computed(() => userStore.currentUser);
// 同时检查localStorage中的token以确保登录状态正确显示
const isLoggedIn = computed(() => currentUser.value || !!localStorage.getItem('access_token'));

// 响应式数据
const searchQuery = ref('');
const loading = ref(false);
const error = ref('');
const resources = ref([]);
const favoritedResourceIds = ref(new Set());  // 已收藏的资源ID集合

// 资源类型映射
const resourceTypes = {
  'book': '书籍',
  'course': '课程',
  'article': '文章',
  'project': '项目',
  'tool': '工具',
  'document': '文档'
};

// 获取资源类型标签
const getResourceTypeLabel = (type) => {
  return resourceTypes[type] || type;
};

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器，添加认证token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// 搜索函数 - 专注于学习资源搜索
const performSearch = async () => {
  const query = searchQuery.value.trim();
  if (!query) {
    // 清空搜索结果
    resources.value = [];
    return;
  }

  loading.value = true;
  error.value = '';
  resources.value = [];

  try {
    // 首先尝试调用全局搜索API
    try {
      const response = await api.get('/search/', {
        params: {
          query,
          type: 'resources'
        }
      });
      
      console.log('全局搜索API响应:', response.data);
      resources.value = Array.isArray(response.data) ? response.data : 
                       response.data.results || 
                       response.data.resources || [];
    } catch (globalSearchError) {
      console.warn('全局搜索API调用失败，尝试直接搜索资源:', globalSearchError);
      
      // 降级方案：直接搜索资源API
      try {
        // 使用正确的API端点，传递search参数
        const response = await api.get('/resources/', {
          params: {
            search: query
          }
        });
        
        console.log('资源搜索API响应:', response.data);
        // 处理响应数据
        if (Array.isArray(response.data)) {
          resources.value = response.data;
        } else if (response.data.results) {
          resources.value = response.data.results;
        } else if (response.data.resources) {
          resources.value = response.data.resources;
        } else {
          resources.value = [];
        }
      } catch (resourceSearchError) {
        console.error('资源搜索失败:', resourceSearchError);
        // 提供友好的错误信息
        error.value = '搜索暂时不可用，请稍后重试';
      }
    }
  } catch (err) {
    console.error('搜索过程中发生错误:', err);
    error.value = '搜索失败，请检查网络连接后重试';
  } finally {
    loading.value = false;
  }
};

// 高亮显示搜索词
const highlightSearchTerm = (text) => {
  if (!text || !searchQuery.value) return text;
  
  const query = searchQuery.value.trim();
  if (!query) return text;
  
  // 创建正则表达式，支持空格分割的多个关键词，使用非贪婪匹配
  const regex = new RegExp(`(${query.replace(/\s+/g, '|')})`, 'gi');
  return text.replace(regex, '<mark class="highlight">$1</mark>');
};

// 检查资源是否已收藏
const isResourceFavorited = (resourceId) => {
  return favoritedResourceIds.value.has(resourceId);
};

// 获取已收藏的资源列表
const fetchFavoritedResources = async () => {
  if (!isLoggedIn.value) return;
  
  try {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    
    const response = await axios.get(`${API_BASE_URL}/favorites/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    // 提取已收藏的资源ID（只处理 resources.Resource 类型）
    const favoritedIds = response.data
      .filter(fav => fav.content_object && fav.content_object.id)
      .map(fav => fav.content_object.id);
    
    favoritedResourceIds.value = new Set(favoritedIds);
  } catch (error) {
    console.error('获取已收藏资源失败:', error);
  }
};

// 监听路由参数，自动执行搜索
onMounted(async () => {
  // 如果从其他页面跳转过来，可能会带搜索参数
  const query = route.query.q;
  
  await fetchFavoritedResources();
  
  if (query) {
    searchQuery.value = query;
    performSearch();
  }
});

// 监听路由变化，当搜索参数改变时重新执行搜索
watch(() => route.query.q, (newQuery) => {
  if (newQuery) {
    searchQuery.value = newQuery;
    performSearch();
  }
});


// 收藏资源方法
const handleFavorite = async (resource) => {
  try {
    // 检查用户是否已登录
    if (!isLoggedIn.value) {
      alert('请先登录！');
      return;
    }
    
    // 从 localStorage 中获取令牌
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('登录状态异常，未获取到有效令牌！');
      return;
    }
    
    await axios.post(`${API_BASE_URL}/favorites/`, {
      resource_type: 'resources.Resource',
      resource_id: resource.id
    }, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    // 添加到已收藏列表
    favoritedResourceIds.value.add(resource.id);
    alert('收藏成功！');
  } catch (error) {
    if (error.response?.status === 400) {
      // 如果已收藏，也添加到已收藏列表
      favoritedResourceIds.value.add(resource.id);
      alert('已收藏该资源，请勿重复操作！');
    } else if (error.response?.status === 401) {
      alert('登录状态失效，请重新登录！');
    } else {
      alert('收藏失败，请检查网络或登录状态！');
    }
  }
};
</script>

<style scoped>
.search-results-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: 80vh;
}



/* 搜索统计样式 */
.search-stats {
  margin-bottom: 20px;
  color: #666;
  font-size: 14px;
}

.loading-text {
  color: #4a90e2;
  font-weight: 500;
}

/* 错误消息样式 */
.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
  border: 1px solid #f5c6cb;
  text-align: center;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 结果区域样式 */
.results-area {
  width: 100%;
}

/* 资源网格布局 */
.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  animation: fadeIn 0.5s ease;
}

/* 资源卡片样式 */
.resource-card {
  background: white;
  border-radius: 12px;
  position: relative;
  padding: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  overflow: hidden;
  height: 100%;
}

.resource-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1), 0 4px 10px rgba(0, 0, 0, 0.08);
}

/* 封面图片容器 */
.resource-cover {
  width: 100%;
  height: 180px;
  overflow: hidden;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.resource-card:hover .cover-image {
  transform: scale(1.08);
}

/* 资源卡片内容区域 */
.resource-card-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}

/* 资源头部 */
.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.resource-header h2 {
  font-size: 1.2rem;
  margin: 0;
  flex: 1;
}

.resource-type {
  background: #e9ecef;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #495057;
}

/* 资源评分 */
.resource-rating {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stars {
  color: #ddd;
}

.stars .filled {
  color: #ffd700;
}

.rating-text {
  font-size: 0.9rem;
  color: #666;
}

/* 资源描述 */
.resource-description {
  color: #6c757d;
  margin: 0;
  line-height: 1.5;
}

/* 资源元信息 */
.resource-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.developer-level {
  color: #6c757d;
  font-size: 0.9rem;
}

.categories {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-tag {
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #495057;
  display: inline-flex;
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

/* 按钮组容器 */
.resource-actions {
  display: flex;
  gap: 12px;
  margin-top: auto;
  align-items: stretch;
}

/* 资源链接 */
.resource-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
  flex: 1;
}

.resource-link:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

/* 收藏按钮样式 */
.favorite-btn {
  background: #f3f4f6;
  color: #4b5563;
  border: 1px solid #e5e7eb;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  flex-shrink: 0;
  white-space: nowrap;
}

.favorite-btn:hover {
  background: #fee2e2;
  color: #dc2626;
  border-color: #fecaca;
}

/* 初始状态样式 */
.initial-state {
  text-align: center;
  padding: 100px 20px;
  color: #666;
}

.initial-icon {
  font-size: 5rem;
  color: #4a90e2;
  margin-bottom: 25px;
  opacity: 0.6;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.05); opacity: 0.8; }
  100% { transform: scale(1); opacity: 0.6; }
}

.initial-state h2 {
  font-size: 2.2rem;
  color: #333;
  margin-bottom: 15px;
  font-weight: 700;
}

.initial-state p {
  font-size: 1.1rem;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

/* 加载指示器样式 */
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #666;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #4a90e2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 无结果提示样式 */
.no-results {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px dashed #dee2e6;
  animation: fadeIn 0.3s ease;
}

/* 搜索词高亮样式 */
:deep(.highlight) {
  background-color: #fff3cd;
  color: #856404;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: 600;
  transition: all 0.2s ease;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-header {
    padding: 15px;
  }
  
  .search-bar-wrapper {
    flex-direction: column;
  }
  
  .search-button {
    width: 100%;
    justify-content: center;
  }
  
  .resources-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .resource-card {
    padding: 16px;
  }
  
  .initial-state {
    padding: 60px 20px;
  }
  
  .initial-icon {
    font-size: 4rem;
  }
  
  .initial-state h2 {
    font-size: 1.8rem;
  }
  
  .loading-indicator {
    padding: 60px 20px;
  }
  
  .spinner {
    width: 40px;
    height: 40px;
  }
  
  .card-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .search-results-container {
    padding: 15px;
  }
  
  .search-input {
    font-size: 14px;
    padding: 10px 12px;
  }
  
  .search-button {
    font-size: 14px;
    padding: 10px 20px;
  }
  
  .resource-title {
    font-size: 1.1rem;
  }
  
  .initial-state h2 {
    font-size: 1.6rem;
  }
  
  .initial-state p {
    font-size: 1rem;
  }
}
</style>