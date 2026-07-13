<template>
  <div class="resource-list-wrapper">
    <div class="resource-list">
      <h1>资源库</h1>

      <!-- 资源列表区域 -->
      <div class="resources-container">
        <div v-if="resources.length === 0 && !loading" class="empty-state">
          <p>暂无资源</p>
        </div>
        <div v-else-if="loading" class="loading-state">
          <p>加载中...</p>
        </div>
        <template v-else>
          <div v-for="resource in resources" :key="resource.id" class="resource-card">
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
            <h2>{{ resource.title }}</h2>
            <div class="resource-type">{{ getResourceTypeLabel(resource.resource_type) }}</div>
          </div>
          
          <!-- 资源评分 -->
          <div class="resource-rating">
            <span class="stars">
              <i v-for="n in 5" :key="n" class="fas fa-star" :class="{ 'filled': n <= resource.rating }"></i>
            </span>
            <span class="rating-text">{{ resource.rating }}/5</span>
          </div>
          
          <!-- 资源描述 -->
          <p class="resource-description">{{ resource.description }}</p>
          
          <!-- 资源元信息 -->
          <div class="resource-meta">
            <!-- 开发者级别 -->
            <span class="developer-level" v-if="resource.target_audience_display || resource.target_audience">
              <i class="fas fa-user"></i> {{ resource.target_audience_display || resource.target_audience }}
            </span>
            
            <!-- 关联分类 -->
            <div class="categories" v-if="resource.categories_display && resource.categories_display.length">
              <span v-for="category in resource.categories_display" :key="category.id" class="category-tag">
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
          
            <!-- 按钮组：查看资源和收藏 -->
            <div class="resource-actions">
              <!-- 资源链接 -->
              <router-link
                :to="{ name: 'ResourceDetail', params: { id: resource.id } }"
                class="resource-link"
              >
                <i class="fas fa-book-open"></i> 查看资源
              </router-link>

              <!-- 新增：收藏按钮（仅登录用户可见且未收藏时显示） -->
              <button 
                v-if="isLoggedIn && !isResourceFavorited(resource.id)" 
                @click="handleFavorite(resource)" 
                class="favorite-btn"
              >
                <i class="fas fa-heart"></i> 收藏
              </button>
            </div>
          </div>
        </div>
        </template>
      </div>

      <!-- 分页组件 -->
      <div v-if="totalPages > 1" class="pagination-container">
        <div class="pagination">
          <button 
            @click="goToPage(currentPage - 1)" 
            :disabled="currentPage === 1"
            class="pagination-btn"
          >
            <i class="fas fa-chevron-left"></i> 上一页
          </button>
          
          <div class="pagination-pages">
            <button
              v-for="page in visiblePages"
              :key="page"
              @click="goToPage(page)"
              :class="['pagination-page', { active: page === currentPage }]"
            >
              {{ page }}
            </button>
          </div>
          
          <button 
            @click="goToPage(currentPage + 1)" 
            :disabled="currentPage === totalPages"
            class="pagination-btn"
          >
            下一页 <i class="fas fa-chevron-right"></i>
          </button>
        </div>
        
        <div class="pagination-info">
          第 {{ currentPage }} / {{ totalPages }} 页，共 {{ totalCount }} 条资源
        </div>
      </div>
    </div>

    <!-- 收藏分类选择模态框 -->
    <div v-if="showCategorySelectModal" class="modal-overlay" @click.self="cancelFavorite">
      <div class="modal-content">
        <h3>选择收藏夹</h3>
        <select v-model="selectedCategoryId" class="category-select">
          <option v-for="category in favoriteCategories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
        <div class="modal-actions">
          <button @click="cancelFavorite" class="cancel-btn">取消</button>
          <button @click="confirmFavorite" class="confirm-btn">确认收藏</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '@/config/api'
import { useUserStore } from '@/stores/user'
import { getFavoriteCategories, addFavorite } from '@/services/favoriteService'
import { 
  getImageCorsAttribute, 
  getImageReferrerPolicy, 
  handleImageError, 
  handleImageLoad 
} from '@/utils/imageUtils'

export default {
  name: 'ResourceList',
  setup() {
    // 响应式数据
    const resources = ref([])                // 当前页资源
    const favoritedResourceIds = ref(new Set())  // 已收藏的资源ID集合
    const currentPage = ref(1)               // 当前页码
    const totalPages = ref(1)               // 总页数
    const totalCount = ref(0)               // 总资源数
    const loading = ref(false)               // 加载状态
    
    // 资源类型映射
    const resourceTypes = {
      'book': '书籍',
      'course': '课程',
      'article': '文章',
      'project': '项目',
      'tool': '工具',
      'document': '文档'
    }
    
    // 获取资源类型标签
    const getResourceTypeLabel = (type) => {
      return resourceTypes[type] || type
    }
    
    // 检查资源是否已收藏
    const isResourceFavorited = (resourceId) => {
      return favoritedResourceIds.value.has(resourceId)
    }
    
    // 获取资源数据
    const fetchResources = async (page = 1) => {
      loading.value = true
      try {
        const response = await axios.get(`${API_BASE_URL}/resources/`, {
          params: {
            page: page,
            page_size: 12
          }
        })
        
        // 处理分页响应数据
        if (response.data.results) {
          // 分页格式：{ count, next, previous, results }
          resources.value = response.data.results.map(resource => ({
            ...resource,
            target_audience_display: resource.target_audience_display || resource.target_audience || ''
          }))
          totalCount.value = response.data.count || 0
          totalPages.value = Math.ceil(totalCount.value / 12) || 1
          currentPage.value = page
        } else {
          // 兼容非分页格式（向后兼容）
          resources.value = response.data.map(resource => ({
            ...resource,
            target_audience_display: resource.target_audience_display || resource.target_audience || ''
          }))
          totalCount.value = resources.value.length
          totalPages.value = 1
        }
        
        // 验证开发者级别数据
        const uniqueLevels = [...new Set(resources.value.map(r => r.target_audience_display || r.target_audience).filter(Boolean))]
        console.log('资源中存在的开发者级别:', uniqueLevels)
      } catch (error) {
        console.error('获取资源列表失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 跳转到指定页码
    const goToPage = (page) => {
      if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
        fetchResources(page)
        // 滚动到顶部
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }
    
    // 计算可见的页码
    const visiblePages = computed(() => {
      const pages = []
      const maxVisible = 5 // 最多显示5个页码按钮
      let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
      let end = Math.min(totalPages.value, start + maxVisible - 1)
      
      // 如果接近末尾，调整起始位置
      if (end - start < maxVisible - 1) {
        start = Math.max(1, end - maxVisible + 1)
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })
    
    // 获取已收藏的资源列表
    const fetchFavoritedResources = async () => {
      if (!isLoggedIn.value) return
      
      try {
        const token = localStorage.getItem('access_token')
        if (!token) return
        
        const response = await axios.get(`${API_BASE_URL}/favorites/`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        // 提取已收藏的资源ID（只处理 resources.Resource 类型）
        const favoritedIds = response.data
          .filter(fav => fav.content_object && fav.content_object.id)
          .map(fav => fav.content_object.id)
        
        favoritedResourceIds.value = new Set(favoritedIds)
      } catch (error) {
        console.error('获取已收藏资源失败:', error)
      }
    }
    
    
    // 组件挂载后加载数据
    onMounted(async () => {
      await fetchResources(1)
      await fetchFavoritedResources()
    })
    
    // 获取用户状态
    const store = useUserStore()
    const currentUser = computed(() => store.currentUser)
    // 同时检查localStorage中的token以确保登录状态正确显示
    const isLoggedIn = computed(() => currentUser.value || !!localStorage.getItem('access_token'))
    
    // 收藏资源方法
    // 收藏分类相关状态
    const showCategorySelectModal = ref(false);
    const favoriteCategories = ref([]);
    const selectedCategoryId = ref(null);
    const resourceToFavorite = ref(null);

    // 处理收藏点击
    const handleFavorite = async (resource) => {
      try {
        // 检查用户是否已登录
        if (!currentUser.value) {
          alert('请先登录！');
          return;
        }
        
        // 加载收藏分类
        favoriteCategories.value = await getFavoriteCategories();
        selectedCategoryId.value = favoriteCategories.value.find(cat => cat.name === '默认收藏夹')?.id || null;
        resourceToFavorite.value = resource;
        showCategorySelectModal.value = true;
      } catch (error) {
        console.error('加载收藏分类失败:', error);
        alert('加载收藏分类失败，请重试！');
      }
    };

    // 确认收藏
    const confirmFavorite = async () => {
      if (!resourceToFavorite.value) return;
      
      try {
        await addFavorite(
          'resources.Resource',
          resourceToFavorite.value.id,
          selectedCategoryId.value
        );
        // 添加到已收藏列表
        favoritedResourceIds.value.add(resourceToFavorite.value.id)
        alert('收藏成功！');
        showCategorySelectModal.value = false;
        resourceToFavorite.value = null;
      } catch (error) {
        if (error.response?.status === 400) {
          // 如果已收藏，也添加到已收藏列表
          favoritedResourceIds.value.add(resourceToFavorite.value.id)
          alert('已收藏该资源，请勿重复操作！');
        } else if (error.response?.status === 401) {
          alert('登录状态失效，请重新登录！');
        } else {
          alert('收藏失败，请检查网络或登录状态！');
        }
        showCategorySelectModal.value = false;
        resourceToFavorite.value = null;
      }
    };

    // 取消收藏操作
    const cancelFavorite = () => {
      showCategorySelectModal.value = false;
      resourceToFavorite.value = null;
    };


    return {
      resources,
      resourceTypes,
      getResourceTypeLabel,
      currentUser,
      isLoggedIn,
      handleFavorite,
      showCategorySelectModal,
      favoriteCategories,
      selectedCategoryId,
      confirmFavorite,
      cancelFavorite,
      handleImageError,
      handleImageLoad,
      getImageCorsAttribute,
      getImageReferrerPolicy,
      isResourceFavorited,
      currentPage,
      totalPages,
      totalCount,
      loading,
      goToPage,
      visiblePages
    }
  }
}
</script>

<style scoped>
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
  padding: 24px;
  min-width: 300px;
  max-width: 90vw;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #111827;
  font-size: 1.25rem;
  font-weight: 600;
}

.category-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 1rem;
  margin-bottom: 16px;
  background: white;
}

.modal-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.cancel-btn,
.confirm-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
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

.confirm-btn:hover {
  background: #2563eb;
}
</style>

<style scoped>
/* 页面整体布局 */
.resource-list {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 资源列表网格 */
.resources-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

/* 资源卡片 */
.resource-card {
  background: white;
  border-radius: 12px;
  padding: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  word-break: break-word;
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
  gap: 12px;
  margin-bottom: 4px;
}

.resource-header h2 {
  font-size: 1.15rem;
  font-weight: 600;
  margin: 0;
  flex: 1;
  color: #1f2937;
  line-height: 1.4;
  word-wrap: break-word;
  overflow-wrap: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 2;
}

.resource-type {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}

/* 资源评分 */
.resource-rating {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
}

.stars {
  color: #e5e7eb;
  font-size: 0.9rem;
}

.stars .filled {
  color: #fbbf24;
}

.rating-text {
  font-size: 0.85rem;
  color: #6b7280;
  font-weight: 500;
}

/* 资源描述 */
.resource-description {
  color: #6b7280;
  margin: 0;
  line-height: 1.6;
  font-size: 0.9rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 3;
}

/* 资源元信息 */
.resource-meta {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 4px;
}

.developer-level {
  color: #6b7280;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.developer-level i {
  color: #9ca3af;
}

.categories {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.category-tag {
  background: #f3f4f6;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.8rem;
  color: #4b5563;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: background-color 0.2s;
}

.category-tag:hover {
  background: #e5e7eb;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .resource-list {
    padding: 15px;
  }
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

/* 空状态和加载状态 */
.empty-state,
.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
  font-size: 1.1rem;
}

/* 分页容器 */
.pagination-container {
  margin-top: 40px;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

/* 分页按钮组 */
.pagination {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

.pagination-btn {
  padding: 10px 20px;
  border: 1px solid #e5e7eb;
  background: white;
  color: #374151;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.pagination-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #d1d5db;
  color: #111827;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 页码按钮组 */
.pagination-pages {
  display: flex;
  gap: 4px;
}

.pagination-page {
  min-width: 40px;
  height: 40px;
  padding: 0 12px;
  border: 1px solid #e5e7eb;
  background: white;
  color: #374151;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination-page:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.pagination-page.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
}

/* 分页信息 */
.pagination-info {
  color: #6b7280;
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .pagination {
    gap: 4px;
  }
  
  .pagination-btn {
    padding: 8px 16px;
    font-size: 0.85rem;
  }
  
  .pagination-page {
    min-width: 36px;
    height: 36px;
    padding: 0 8px;
    font-size: 0.85rem;
  }
  
  .pagination-info {
    font-size: 0.85rem;
    text-align: center;
  }
}
</style>