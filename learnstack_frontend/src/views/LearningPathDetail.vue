<template>
  <div class="learning-path-detail-container">
    <!-- 页面加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载学习路径中...</p>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <button @click="fetchLearningPath" class="retry-button">重试</button>
    </div>

    <!-- 学习路径内容 -->
    <div v-else-if="learningPath" class="path-content">
        <!-- 面包屑导航 -->
        <div class="breadcrumb">
          <router-link to="/allCategories">所有分类</router-link>
          <span v-if="parentCategory">
            <span> > </span>
            <router-link :to="`/categories/${parentCategory.id}`">{{ parentCategory.name }}</router-link>
          </span>
          <span v-if="learningPath && learningPath.technology" class="current-page">
            <span> > </span>
            {{ learningPath.technology.name }}
          </span>
        </div>
        
        <!-- 学习进度概览已移至Dashboard页面 -->
      <!-- 页面头部 -->
      <section class="path-hero">
        <div class="hero-left">
          <div class="technology-icon">
            <img 
              v-if="learningPath && learningPath.technology && learningPath.technology.icon_image_url"
              :src="learningPath.technology.icon_image_url" 
              :alt="learningPath.technology.name"
              class="technology-icon-image"
            />
            <div 
              v-else
              class="technology-icon-placeholder"
            >
              {{ (learningPath && learningPath.technology && learningPath.technology.name) ? learningPath.technology.name.charAt(0) : '?' }}
            </div>
          </div>
          <div class="path-title-section">
            <p class="hero-eyebrow">学习路径</p>
            <h1 class="path-title">{{ (learningPath && learningPath.technology && learningPath.technology.name) || '学习路径' }}</h1>
            <p class="path-description">{{ (learningPath && learningPath.description) || '暂无描述' }}</p>
            <div class="hero-actions">
              <button v-if="isAuthenticated" @click="exportToPDF" class="export-pdf-btn">
                <i class="fas fa-file-pdf"></i>
                导出学习计划
              </button>
              <router-link v-if="isAuthenticated" to="/resources/submit" class="submit-btn">
                <i class="fas fa-plus"></i> 投稿资源
              </router-link>
            </div>
          </div>
        </div>
        <div class="hero-stats grid">
          <div class="stat-card">
            <span class="stat-label">学习阶段</span>
            <span class="stat-value">{{ (learningPath.stages && learningPath.stages.length) || 0 }}</span>
          </div>
          <div class="stat-card">
            <span class="stat-label">推荐资源</span>
            <span class="stat-value">{{ calculateTotalResources() }}</span>
          </div>
          <div class="stat-card">
            <span class="stat-label">创建时间</span>
            <span class="stat-value">{{ (learningPath.technology && learningPath.technology.created_at && learningPath.technology.created_at.slice(0, 10)) || '--' }}</span>
          </div>
        </div>
      </section>

      <section class="stages-layout">
        <aside class="sidebar-section">
          <div class="stage-nav" v-if="learningPath.stages && learningPath.stages.length">
          <h3>阶段导航</h3>
          <ul>
            <li
              v-for="(stage, index) in learningPath.stages"
              :key="stage.id"
              @click="scrollToStage(stage.id)"
            >
              <span>{{ index + 1 }}</span>
              {{ stage.title }}
            </li>
          </ul>
          </div>

          <!-- 学习统计卡片 -->
          <div class="learning-stats-card" v-if="learningPath && isAuthenticated">
            <h3>学习统计</h3>
            <div class="stats-content">
              <div class="stat-item">
                <div class="stat-icon completed">
                  <i class="fas fa-check-circle"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ completedStagesCount }}</div>
                  <div class="stat-label">已完成阶段</div>
                </div>
              </div>
              <div class="stat-item">
                <div class="stat-icon pending">
                  <i class="far fa-circle"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ pendingStagesCount }}</div>
                  <div class="stat-label">未完成阶段</div>
                </div>
              </div>
              <div class="stat-item">
                <div class="stat-icon favorites">
                  <i class="fas fa-heart"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ favoritedResourcesCount }}</div>
                  <div class="stat-label">已收藏资源</div>
                </div>
              </div>
            </div>
            <div class="progress-bar-container">
              <div class="progress-label">
                <span>学习进度</span>
                <span class="progress-percentage">{{ learningProgressPercentage }}%</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: learningProgressPercentage + '%' }"></div>
              </div>
            </div>
          </div>
        </aside>

        <!-- 阶段详情内容 -->
        <div class="stages-content">
        <div 
          v-for="(stage, index) in learningPath.stages" 
          :key="stage.id"
          :id="`stage-${stage.id}`"
          class="stage-section"
        >
          <div class="stage-header">
            <div class="stage-number">{{ index + 1 }}</div>
            <h2 class="stage-title">{{ stage.title }}</h2>
            <button 
              :class="['stage-complete-btn', { active: isStageCompleted(stage.id) }]"
              @click="toggleStageCompletion(stage)"
              :disabled="!isAuthenticated"
            >
              <i class="fas fa-check-circle"></i>
              <span>{{ isStageCompleted(stage.id) ? '已完成' : (isAuthenticated ? '标记完成' : '登录后标记') }}</span>
            </button>
          </div>
          
          <div v-if="stage.description" class="stage-description">
            {{ stage.description }}
          </div>

          <!-- 学习资源列表 -->
          <div class="resources-section">
            <h3 class="resources-title">推荐学习资源</h3>
            <!-- 资源网格 -->
            <div v-if="stage.recommended_resources && stage.recommended_resources.length > 0" class="resources-grid">
              <div 
                v-for="resource in stage.recommended_resources" 
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
                  <h2>{{ resource.title }}</h2>
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
                    v-if="isAuthenticated && !isResourceFavorited(resource.id)" 
                    @click="handleFavorite(resource)" 
                    class="favorite-btn"
                  >
                    <i class="fas fa-heart"></i> 收藏
                  </button>
                </div>
                </div>
              </div>
            </div>
            
            <!-- 无资源提示 -->
            <div v-else class="no-resources">

              <p>当前阶段暂无推荐资源</p>
            </div>
          </div>
        </div>
        </div>
      </section>


    </div>

    <!-- 空状态 -->
    <div v-else class="empty-container">
      <h3>未找到学习路径</h3>
      <p>该技术暂时没有设置学习路径</p>
      <router-link to="/allCategories" class="back-link">返回分类列表</router-link>
    </div>

    <div v-if="showCategorySelectModal" class="favorite-modal-overlay" @click.self="cancelFavorite">
    <div class="favorite-modal">
      <h3>选择收藏夹</h3>
      <select v-model="selectedCategoryId" class="favorite-category-select">
        <option 
          v-for="category in favoriteCategories" 
          :key="category.id" 
          :value="category.id"
        >
          {{ category.name }}
        </option>
      </select>
      <div class="favorite-modal-actions">
        <button @click="cancelFavorite" class="favorite-cancel-btn">取消</button>
        <button @click="confirmFavorite" class="favorite-confirm-btn">确认收藏</button>
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getLearningPathByCategory, markStageCompleted, unmarkStageCompleted, getUserProgress, recordStudyTime } from '../services/learningPathService';
import axios from 'axios';
import { API_BASE_URL } from '@/config/api';
import { useUserStore } from '@/stores/user';
import html2pdf from 'html2pdf.js';
import { 
  getImageCorsAttribute, 
  getImageReferrerPolicy, 
  handleImageError, 
  handleImageLoad 
} from '@/utils/imageUtils';
import { getFavoriteCategories, addFavorite } from '@/services/favoriteService';
import { initStudyTimeTracker, cleanupStudyTimeTracker, recordStageCompletionTime } from '@/utils/studyTimeTracker';

const route = useRoute();
const router = useRouter();

// 响应式数据
const learningPath = ref(null);
const loading = ref(true);
const error = ref('');
const userProgress = ref([]);
const parentCategory = ref(null);
const favoritedResourceIds = ref(new Set());  // 已收藏的资源ID集合
const showCategorySelectModal = ref(false);
const favoriteCategories = ref([]);
const selectedCategoryId = ref(null);
const resourceToFavorite = ref(null);


const userStore = useUserStore();
const currentUser = computed(() => userStore.currentUser);
// 同时检查localStorage中的token和store中的用户状态
const isAuthenticated = computed(() => currentUser.value || !!localStorage.getItem('access_token'));

// 从路由参数获取分类ID
const categoryId = computed(() => route.params.categoryId);


// 获取父分类信息
const fetchParentCategory = async (technologyId) => {
  try {
    // 首先获取当前技术分类的完整信息
    const response = await axios.get(`${API_BASE_URL}/categories/${technologyId}/`);
    if (response.data && response.data.parent) {
      const parentResponse = await axios.get(`${API_BASE_URL}/categories/${response.data.parent}/`);
      parentCategory.value = parentResponse.data;
    }
  } catch (err) {
    console.error('获取父分类失败:', err);
    // 即使获取父分类失败也不影响页面显示
  }
};

// 获取学习路径数据
const fetchLearningPath = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    console.log(`Fetching learning path for category ID: ${categoryId.value}`);
    const response = await getLearningPathByCategory(categoryId.value);
    learningPath.value = response.data;
    
    // 获取父分类信息
    if (learningPath.value && learningPath.value.technology && learningPath.value.technology.id) {
      await fetchParentCategory(learningPath.value.technology.id);
    }
    
    // 获取用户学习进度
    if (isAuthenticated.value) {
      fetchUserProgress();
    }
  } catch (err) {
    console.error('获取学习路径失败:', err);
    const detailMsg = err.response && err.response.data && err.response.data.detail;
    error.value = detailMsg || '获取学习路径失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};

// 获取用户学习进度
const fetchUserProgress = async () => {
  try {
    console.log('获取用户学习进度');
    
    // 如果用户已登录，优先从后端获取进度
    if (isAuthenticated.value) {
      try {
        const response = await getUserProgress(categoryId.value);
        userProgress.value = response.data || [];
        console.log('从后端获取学习进度:', userProgress.value);
        
        // 同步到localStorage作为备份
        try {
          localStorage.setItem(`user_progress_${categoryId.value}`, JSON.stringify(userProgress.value));
        } catch (storageErr) {
          console.warn('保存进度到localStorage失败:', storageErr);
        }
        
        return;
      } catch (apiErr) {
        console.warn('从后端获取学习进度失败，尝试从localStorage加载:', apiErr);
        // 如果后端API失败，尝试从localStorage加载
      }
    }
    
    // 如果未登录或后端API失败，从localStorage加载进度
    const savedProgress = localStorage.getItem(`user_progress_${categoryId.value}`);
    if (savedProgress) {
      try {
      userProgress.value = JSON.parse(savedProgress);
      console.log('从localStorage加载进度:', userProgress.value);
      } catch (parseErr) {
        console.error('解析localStorage进度数据失败:', parseErr);
        userProgress.value = [];
      }
    } else {
      userProgress.value = [];
    }
  } catch (err) {
    console.error('获取用户学习进度失败:', err);
    // 出错时不影响页面正常显示，继续使用空进度
    userProgress.value = [];
  }
};

// 检查阶段是否已完成
const isStageCompleted = (stageId) => {
  return userProgress.value.some(progress => progress.stage_id === stageId && progress.is_completed);
};

// 切换阶段完成状态
const toggleStageCompletion = async (stage) => {
  if (!isAuthenticated.value) {
    if (confirm('请先登录以标记学习进度')) {
      router.push({ path: '/login', query: { redirect: route.fullPath } });
    }
    return;
  }

  try {
    const isCurrentlyCompleted = isStageCompleted(stage.id);
    
    if (isCurrentlyCompleted) {
      // 取消标记完成
      await unmarkStageCompleted(stage.id);
      // 更新本地进度状态
      const progressIndex = userProgress.value.findIndex(p => p.stage_id === stage.id);
      if (progressIndex !== -1) {
        userProgress.value[progressIndex].is_completed = false;
      }
      alert('已取消完成标记');
    } else {
      // 标记为完成
      await markStageCompleted(stage.id, stage.title, stage.order || 1);
      // 更新本地进度状态
      const existingProgress = userProgress.value.find(p => p.stage_id === stage.id);
      if (existingProgress) {
        existingProgress.is_completed = true;
      } else {
        userProgress.value.push({
          stage_id: stage.id,
          stage_title: stage.title,
          stage_order: stage.order || 1,
          is_completed: true,
          completed_at: new Date().toISOString()
        });
      }
      
      // 自动记录学习阶段完成时的学习时长（0.5小时）
      if (isAuthenticated.value) {
        try {
          await recordStageCompletionTime(recordStudyTime, 0.5);
        } catch (err) {
          console.warn('自动记录学习时长失败:', err);
          // 不影响主流程，静默失败
        }
      }
      
      alert('已标记为完成');
    }
    
    // 每次修改后立即保存到localStorage和同步到后端
    try {
      localStorage.setItem(`user_progress_${categoryId.value}`, JSON.stringify(userProgress.value));
      console.log('进度已更新并保存到localStorage');
      
      // 如果后端API调用成功，进度已经同步到后端
      // 这里localStorage作为本地备份
    } catch (storageErr) {
      console.error('保存进度到localStorage失败:', storageErr);
    }
  } catch (err) {
    console.error('更新学习进度失败:', err);
    // 即使后端API失败，我们仍然更新本地状态，提供更好的用户体验
    try {
      const isCurrentlyCompleted = isStageCompleted(stage.id);
      if (isCurrentlyCompleted) {
        const progressIndex = userProgress.value.findIndex(p => p.stage_id === stage.id);
        if (progressIndex !== -1) {
          userProgress.value[progressIndex].is_completed = false;
        }
      } else {
        const existingProgress = userProgress.value.find(p => p.stage_id === stage.id);
        if (existingProgress) {
          existingProgress.is_completed = true;
        } else {
          userProgress.value.push({
            stage_id: stage.id,
            stage_title: stage.title,
            stage_order: stage.order || 1,
            is_completed: true,
            completed_at: new Date().toISOString()
          });
        }
      }
      // 保存到localStorage
      localStorage.setItem(`user_progress_${categoryId.value}`, JSON.stringify(userProgress.value));
      alert('本地进度已更新，但与服务器同步失败');
    } catch {
      alert('操作失败，请稍后重试');
    }
  }
};

const scrollToStage = (stageId) => {
  const el = document.getElementById(`stage-${stageId}`);
  if (el) {
    const offset = 90;
    const elementTop = el.getBoundingClientRect().top + window.pageYOffset;
    window.scrollTo({
      top: elementTop - offset,
      behavior: 'smooth'
    });
  }
};





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

// 检查资源是否已收藏
const isResourceFavorited = (resourceId) => {
  return favoritedResourceIds.value.has(resourceId);
};

// 获取已收藏的资源列表
const fetchFavoritedResources = async () => {
  if (!isAuthenticated.value) return;
  
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

// 处理收藏功能
const handleFavorite = async (resource) => {
  try {
    if (!currentUser.value) {
      alert('请先登录！');
      return;
    }

    favoriteCategories.value = await getFavoriteCategories();
    if (!favoriteCategories.value.length) {
      alert('暂未创建收藏夹，请先在收藏中心创建。');
      return;
    }
    const defaultCategory = favoriteCategories.value.find(cat => cat.name === '默认收藏夹');
    selectedCategoryId.value = defaultCategory ? defaultCategory.id : favoriteCategories.value[0].id;
    resourceToFavorite.value = resource;
    showCategorySelectModal.value = true;
  } catch (error) {
    console.error('加载收藏分类失败:', error);
    alert('加载收藏分类失败，请稍后重试。');
  }
};

const confirmFavorite = async () => {
  if (!resourceToFavorite.value) return;
  try {
    await addFavorite(
      'resources.Resource',
      resourceToFavorite.value.id,
      selectedCategoryId.value
    );
    favoritedResourceIds.value.add(resourceToFavorite.value.id);
    alert('收藏成功！');
    showCategorySelectModal.value = false;
    resourceToFavorite.value = null;
  } catch (error) {
    if (error.response && error.response.status === 400) {
      favoritedResourceIds.value.add(resourceToFavorite.value.id);
      alert('已收藏该资源，请勿重复操作！');
    } else if (error.response && error.response.status === 401) {
      alert('登录状态失效，请重新登录！');
    } else {
      alert('收藏失败，请检查网络或登录状态！');
    }
    showCategorySelectModal.value = false;
    resourceToFavorite.value = null;
  }
};

const cancelFavorite = () => {
  showCategorySelectModal.value = false;
  resourceToFavorite.value = null;
};

// 计算总资源数量
const calculateTotalResources = () => {
  if (!learningPath.value || !learningPath.value.stages || learningPath.value.stages.length === 0) {
    return 0;
  }
  
  let totalResources = 0;
  learningPath.value.stages.forEach(stage => {
    if (stage.recommended_resources && stage.recommended_resources.length > 0) {
      totalResources += stage.recommended_resources.length;
    }
  });
  
  return totalResources;
};

// 计算已完成阶段数
const completedStagesCount = computed(() => {
  if (!learningPath.value || !learningPath.value.stages) {
    return 0;
  }
  return learningPath.value.stages.filter(stage => isStageCompleted(stage.id)).length;
});

// 计算未完成阶段数
const pendingStagesCount = computed(() => {
  if (!learningPath.value || !learningPath.value.stages) {
    return 0;
  }
  const total = learningPath.value.stages.length;
  const completed = completedStagesCount.value;
  return total - completed;
});

// 计算已收藏的资源数（在当前学习路径中）
const favoritedResourcesCount = computed(() => {
  if (!learningPath.value || !learningPath.value.stages) {
    return 0;
  }
  let count = 0;
  learningPath.value.stages.forEach(stage => {
    if (stage.recommended_resources) {
      stage.recommended_resources.forEach(resource => {
        if (isResourceFavorited(resource.id)) {
          count++;
        }
      });
    }
  });
  return count;
});

// 计算学习进度百分比
const learningProgressPercentage = computed(() => {
  if (!learningPath.value || !learningPath.value.stages || learningPath.value.stages.length === 0) {
    return 0;
  }
  const total = learningPath.value.stages.length;
  const completed = completedStagesCount.value;
  return Math.round((completed / total) * 100);
});


// 导出学习路径为PDF
const exportToPDF = () => {
  if (!isAuthenticated.value) {
    alert('请先登录后再导出学习计划');
    return;
  }
  
  if (!learningPath.value) {
    alert('学习路径数据未加载完成，无法导出PDF');
    return;
  }

  // 创建一个临时的PDF内容容器
  const pdfContent = document.createElement('div');
  pdfContent.style.padding = '20px';
  pdfContent.style.maxWidth = '210mm';
  pdfContent.style.margin = '0 auto';
  pdfContent.style.backgroundColor = 'white';
  pdfContent.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
  
  // 添加学习路径标题和描述
  const header = document.createElement('div');
  header.style.textAlign = 'center';
  header.style.marginBottom = '30px';
  header.style.paddingBottom = '20px';
  header.style.borderBottom = '2px solid #e0e0e0';
  
  const title = document.createElement('h1');
  const techName = learningPath.value && learningPath.value.technology && learningPath.value.technology.name;
  title.textContent = techName || '学习路径';
  title.style.color = '#333';
  title.style.marginBottom = '15px';
  
  const description = document.createElement('p');
  description.textContent = learningPath.value.description || '暂无描述';
  description.style.color = '#666';
  description.style.fontSize = '16px';
  description.style.lineHeight = '1.6';
  
  header.appendChild(title);
  header.appendChild(description);
  pdfContent.appendChild(header);
  
  // 添加学习路径统计信息
  const statsSection = document.createElement('div');
  statsSection.style.display = 'flex';
  statsSection.style.justifyContent = 'center';
  statsSection.style.gap = '40px';
  statsSection.style.marginBottom = '30px';
  statsSection.style.padding = '20px';
  statsSection.style.backgroundColor = '#f8f9fa';
  statsSection.style.borderRadius = '8px';
  
  const stagesStat = document.createElement('div');
  stagesStat.style.textAlign = 'center';
  stagesStat.innerHTML = `
    <div style="font-size: 24px; font-weight: bold; color: #4285f4;">${(learningPath.value.stages && learningPath.value.stages.length) || 0}</div>
    <div style="color: #666; margin-top: 5px;">学习阶段</div>
  `;
  
  const resourcesStat = document.createElement('div');
  resourcesStat.style.textAlign = 'center';
  resourcesStat.innerHTML = `
    <div style="font-size: 24px; font-weight: bold; color: #4285f4;">${calculateTotalResources()}</div>
    <div style="color: #666; margin-top: 5px;">学习资源</div>
  `;
  
  statsSection.appendChild(stagesStat);
  statsSection.appendChild(resourcesStat);
  pdfContent.appendChild(statsSection);
  
  // 添加每个阶段的内容
  if (learningPath.value.stages && learningPath.value.stages.length) {
    learningPath.value.stages.forEach((stage, index) => {
    const stageSection = document.createElement('div');
    stageSection.style.marginBottom = '40px';
    
    const stageHeader = document.createElement('div');
    stageHeader.style.display = 'flex';
    stageHeader.style.alignItems = 'center';
    stageHeader.style.marginBottom = '15px';
    
    const stageNumber = document.createElement('div');
    stageNumber.textContent = index + 1;
    stageNumber.style.width = '30px';
    stageNumber.style.height = '30px';
    stageNumber.style.borderRadius = '50%';
    stageNumber.style.backgroundColor = '#4285f4';
    stageNumber.style.color = 'white';
    stageNumber.style.display = 'flex';
    stageNumber.style.alignItems = 'center';
    stageNumber.style.justifyContent = 'center';
    stageNumber.style.fontWeight = 'bold';
    stageNumber.style.marginRight = '15px';
    
    const stageTitle = document.createElement('h2');
    stageTitle.textContent = stage.title;
    stageTitle.style.color = '#333';
    stageTitle.style.margin = 0;
    
    stageHeader.appendChild(stageNumber);
    stageHeader.appendChild(stageTitle);
    stageSection.appendChild(stageHeader);
    
    if (stage.description) {
      const stageDesc = document.createElement('p');
      stageDesc.textContent = stage.description;
      stageDesc.style.color = '#666';
      stageDesc.style.lineHeight = '1.6';
      stageDesc.style.marginBottom = '20px';
      stageSection.appendChild(stageDesc);
    }
    
    // 添加资源列表
    if (stage.recommended_resources && stage.recommended_resources.length > 0) {
      const resourcesHeader = document.createElement('h3');
      resourcesHeader.textContent = '推荐学习资源';
      resourcesHeader.style.color = '#333';
      resourcesHeader.style.marginBottom = '15px';
      stageSection.appendChild(resourcesHeader);
      
      const resourcesList = document.createElement('div');
      resourcesList.style.borderLeft = '3px solid #e0e0e0';
      resourcesList.style.paddingLeft = '20px';
      
      stage.recommended_resources.forEach(resource => {
        const resourceItem = document.createElement('div');
        resourceItem.style.marginBottom = '20px';
        
        const resourceTitle = document.createElement('div');
        resourceTitle.innerHTML = `
          <strong style="color: #333;">${resource.title}</strong>
          <span style="background: #e9ecef; padding: 3px 8px; border-radius: 4px; font-size: 12px; margin-left: 10px; color: #495057;">${getResourceTypeLabel(resource.resource_type)}</span>
        `;
        
        const resourceDetails = document.createElement('div');
        resourceDetails.style.marginTop = '8px';
        
        if (resource.description) {
          const desc = document.createElement('p');
          desc.textContent = resource.description;
          desc.style.color = '#666';
          desc.style.lineHeight = '1.5';
          desc.style.margin = '0 0 8px 0';
          resourceDetails.appendChild(desc);
        }
        
        if (resource.url) {
          const url = document.createElement('div');
          url.innerHTML = `<strong>链接:</strong> <a href="${resource.url}" style="color: #4285f4; text-decoration: none;">${resource.url}</a>`;
          url.style.color = '#666';
          resourceDetails.appendChild(url);
        }
        
        if (resource.rating) {
          const rating = document.createElement('div');
          rating.innerHTML = `<strong>评分:</strong> ${resource.rating}/5`;
          rating.style.color = '#666';
          rating.style.marginTop = '5px';
          resourceDetails.appendChild(rating);
        }
        
        resourceItem.appendChild(resourceTitle);
        resourceItem.appendChild(resourceDetails);
        resourcesList.appendChild(resourceItem);
      });
      
      stageSection.appendChild(resourcesList);
    }
    
    pdfContent.appendChild(stageSection);
  });
  }
  
  // 将临时容器添加到body
  document.body.appendChild(pdfContent);
  
  // 配置html2pdf选项
  const opt = {
    margin: 10,
    filename: `${(learningPath.value.technology && learningPath.value.technology.name) || '学习路径'}_学习计划.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  };
  
  // 生成PDF并下载
  html2pdf().set(opt).from(pdfContent).save().then(() => {
    // 下载完成后移除临时容器
    document.body.removeChild(pdfContent);
    console.log('PDF导出成功');
  }).catch(err => {
    console.error('PDF导出失败:', err);
    alert('PDF导出失败，请稍后重试');
    document.body.removeChild(pdfContent);
  });
};

// 移除showToast函数，与ResourceList.vue保持一致使用alert

  // 页面卸载时保存用户进度和清理学习时长跟踪
  onBeforeUnmount(() => {
    // 清理学习时长跟踪
    cleanupStudyTimeTracker();
    
    // 将用户进度保存到localStorage，以便刷新页面后可以恢复
    try {
      if (userProgress.value.length > 0) {
        localStorage.setItem(`user_progress_${categoryId.value}`, JSON.stringify(userProgress.value));
        console.log('进度已保存到localStorage');
      }
    } catch (err) {
      console.error('保存进度到localStorage失败:', err);
    }
  });

// 初始化
// 实时学习时长显示（用于实时更新显示）
const currentStudyTime = ref(0);

// 初始化学习时长跟踪（仅登录用户）
const initStudyTimeTracking = () => {
  if (isAuthenticated.value) {
    // 创建记录学习时长的回调函数
    const recordCallback = async (hours) => {
      try {
        await recordStudyTime(hours);
        console.log(`自动记录学习时长: ${hours.toFixed(2)}小时`);
        // 记录后重置当前显示时长
        currentStudyTime.value = 0;
      } catch (err) {
        console.error('记录学习时长失败:', err);
        throw err;
      }
    };
    
    // 创建显示更新回调函数（实时显示当前累计时长）
    const displayUpdateCallback = (hours) => {
      currentStudyTime.value = hours;
      // 可以在这里更新UI显示，比如在页面上显示"当前学习时长: X小时"
      console.log(`当前累计学习时长: ${hours.toFixed(2)}小时`);
    };
    
    // 初始化跟踪
    initStudyTimeTracker(recordCallback, displayUpdateCallback);
  }
};

onMounted(async () => {
  // 初始化学习时长跟踪
  initStudyTimeTracking();
  await fetchLearningPath();
  await fetchFavoritedResources();
});
</script>

<style scoped>
.learning-path-detail-container {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 20px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 加载状态 */
.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
  padding: 40px 20px;
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

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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

.back-link {
  display: inline-block;
  margin-top: 20px;
  padding: 10px 20px;
  background-color: #4285f4;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.back-link:hover {
  background-color: #3367d6;
}

/* 学习路径内容 */
.path-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 面包屑导航 */
.breadcrumb {
  margin-bottom: 20px;
  color: #6b7280;
  font-size: 0.9rem;
}

.breadcrumb a {
  color: #2563eb;
  text-decoration: none;
  transition: color 0.2s;
}

.breadcrumb a:hover {
  text-decoration: underline;
  color: #1d4ed8;
}

.breadcrumb span {
  margin: 0 5px;
}

.breadcrumb .current-page {
  color: #374151;
  font-weight: 500;
}

.breadcrumb .current-page span:first-child {
  color: #6b7280;
  font-weight: normal;
}

/* 学习进度概览样式已移至Dashboard页面 */

/* 页面头部 */
.path-hero {
  background: linear-gradient(120deg, #312e81, #4338ca, #6366f1);
  color: #fff;
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 25px 50px rgba(79, 70, 229, 0.25);
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-left {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.technology-icon {
  width: 100px;
  height: 100px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(8px);
  border: 2px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  flex-shrink: 0;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
}

.technology-icon-image {
  width: 64px;
  height: 64px;
  object-fit: contain;
}

.technology-icon-placeholder {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: bold;
}

.path-title-section {
  flex: 1;
}

.hero-eyebrow {
  margin: 0;
  font-size: 0.85rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.7);
}

.path-title {
  font-size: 2.4rem;
  margin: 0 0 10px 0;
  font-weight: 700;
}

.path-description {
  font-size: 1.1rem;
  opacity: 0.9;
  line-height: 1.6;
  margin: 0;
  max-width: 600px;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}

.export-pdf-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #ff6b6b, #ee5a52);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0;
  align-self: flex-start;
  flex-shrink: 0;
}

.export-pdf-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
  background: linear-gradient(135deg, #ff5252, #e53935);
}

.export-pdf-btn:active {
  transform: translateY(0);
}

.hero-stats.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 1rem;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-label {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
}

.stat-value {
  display: block;
  font-size: 1.8rem;
  font-weight: 600;
  color: #fff;
}

.stages-layout {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  gap: 1.5rem;
}

.sidebar-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  position: sticky;
  top: 90px;
  align-self: flex-start;
}

.stage-nav {
  background: #fff;
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: 0 12px 25px rgba(15, 23, 42, 0.08);
}

.stage-nav h3 {
  margin: 0 0 0.9rem;
  font-size: 1rem;
  color: #0f172a;
}

.stage-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.stage-nav li {
  padding: 0.5rem 0.75rem;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  color: #475569;
  transition: background 0.2s;
}

.stage-nav li span {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: #e0e7ff;
  color: #312e81;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.stage-nav li:hover {
  background: #eef2ff;
  color: #1e1b4b;
}

/* 学习统计卡片样式 */
.learning-stats-card {
  background: #fff;
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: 0 12px 25px rgba(15, 23, 42, 0.08);
}

.learning-stats-card h3 {
  margin: 0 0 1rem;
  font-size: 1rem;
  color: #0f172a;
  font-weight: 600;
}

.stats-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 10px;
  transition: background-color 0.2s;
}

.stat-item:hover {
  background: #f8f9fa;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.stat-icon.completed {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
}

.stat-icon.pending {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.stat-icon.favorites {
  background: linear-gradient(135deg, #ff6b6b, #ee5a52);
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 1.3rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.8rem;
  color: #64748b;
  margin-top: 2px;
}

.progress-bar-container {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  color: #475569;
}

.progress-percentage {
  font-weight: 600;
  color: #4285f4;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4285f4, #667eea);
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* 投稿按钮样式 */
.submit-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-left: auto;
  text-decoration: none;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
  background: linear-gradient(135deg, #45a049, #3d8b40);
}

/* 学习进度概览相关样式已清理 */

/* 阶段详情内容 */
.stages-content {
  margin-bottom: 40px;
}

.stage-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  scroll-margin-top: 140px;
}

.stage-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.stage-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #4285f4;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: 700;
  flex-shrink: 0;
}

.stage-title {
  flex: 1;
  font-size: 1.8rem;
  margin: 0;
  color: #333;
}

.stage-description {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #666;
  padding: 0 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

/* 资源部分 */
.resources-section {
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  padding: 0 20px;
}

.resources-title {
  font-size: 1.5rem;
  margin: 15px 0;
  color: #333;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

/* 资源卡片样式 */
.resource-card {
  background: white;
  border-radius: 12px;
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

/* 标记完成按钮样式 */
.stage-complete-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
}

.stage-complete-btn:hover:not(:disabled) {
  background: #e9ecef;
  border-color: #dee2e6;
}

.stage-complete-btn.active {
  background: #4CAF50;
  color: white;
  border-color: #45a049;
}

.stage-complete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

.favorite-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 1300;
}

.favorite-modal {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.2);
}

.favorite-modal h3 {
  margin: 0 0 16px;
  font-size: 1.1rem;
  color: #111827;
  font-weight: 600;
}

.favorite-category-select {
  width: 100%;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 0.95rem;
  margin-bottom: 18px;
}

.favorite-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.favorite-cancel-btn,
.favorite-confirm-btn {
  border: none;
  border-radius: 8px;
  padding: 8px 20px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.2s;
}

.favorite-cancel-btn {
  background: #f3f4f6;
  color: #4b5563;
}

.favorite-cancel-btn:hover {
  background: #e5e7eb;
}

.favorite-confirm-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.25);
}

.favorite-confirm-btn:hover {
  background: linear-gradient(135deg, #5a67d8, #6b46c1);
}

.no-resources {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

/* 相关学习路径 */
.related-paths-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.related-paths-title {
  font-size: 1.5rem;
  margin-bottom: 20px;
  color: #333;
}

.related-paths-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

/* 移除toast样式，与ResourceList.vue保持一致使用alert */

/* 响应式设计 */
@media (max-width: 768px) {
  .path-hero {
    padding: 24px;
  }
  .hero-left {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  .hero-actions {
    justify-content: center;
  }
  .stages-layout {
    grid-template-columns: 1fr;
  }
  .sidebar-section {
    position: static;
  }
  .stage-nav {
    position: static;
  }
  /* 学习统计信息响应式 */
  .path-stats {
    flex-direction: column;
    gap: 15px;
  }
  
  .stat-item {
    padding: 12px 20px;
  }
  
  .stat-number {
    font-size: 1.5rem;
  }
  
  .stat-item i {
    width: 35px;
    height: 35px;
    font-size: 1.2rem;
  }
  .path-header {
    padding: 30px 20px;
  }
  
  .path-header-info {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .technology-icon {
    margin-right: 0;
    margin-bottom: 20px;
  }
  
  .path-title {
    font-size: 2rem;
  }
  
  .stage-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .stage-title {
    font-size: 1.5rem;
  }
  
  .resources-grid {
    grid-template-columns: 1fr;
  }
  
  .resource-card {
    min-height: auto;
  }
}

@media (max-width: 480px) {
  .path-header {
    padding: 20px 15px;
  }
  
  .path-title {
    font-size: 1.8rem;
  }
  
  .stage-section {
    padding: 20px 15px;
  }
  
  .stage-number {
    width: 35px;
    height: 35px;
    font-size: 1rem;
  }
  
  .stage-title {
    font-size: 1.3rem;
  }
  
  .stage-complete-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>