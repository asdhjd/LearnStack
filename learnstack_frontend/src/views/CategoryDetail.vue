<template>
  <div class="category-page" v-if="category.id">
    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <router-link to="/allCategories">所有分类</router-link>
      <span class="current-page">
        <span> > </span>
        {{ category.name }}
      </span>
    </div>

    <section class="hero">
      <div class="hero-icon">
        <img 
          v-if="category.icon_image_url"
          :src="category.icon_image_url" 
          :alt="category.name"
          class="hero-icon-image"
        />
        <div 
          v-else
          class="hero-icon-placeholder"
        >
          {{ category.name.charAt(0) }}
        </div>
      </div>
      <div class="hero-content">
        <p class="hero-eyebrow">分类详情</p>
        <h1>{{ category.name }}</h1>
        <p class="hero-subtitle" v-if="category.description">{{ category.description }}</p>
        <div class="hero-stats">
          <span><strong>{{ (category.subcategories && category.subcategories.length) || 0 }}</strong> 学习条目</span>
        </div>
      </div>
      <div class="hero-actions">
        <button class="primary-btn" @click="goToAllCategories">
          浏览全部分类
        </button>
        <button class="secondary-btn" @click="goToCommunity">
          去社区讨论
        </button>
      </div>
    </section>

    <section class="details-grid">
      <aside class="sidebar-section">
        <div class="panel overview-panel">
          <div class="panel-header">
            <h2>分类概览</h2>
            <span class="panel-label">学习地图</span>
          </div>
          <div class="mini-card-list">
            <div class="mini-card">
              <div class="mini-icon">
                <i class="fas fa-layer-group"></i>
              </div>
              <div class="mini-info">
                <p class="mini-value">{{ (category.subcategories && category.subcategories.length) || 0 }}</p>
                <p class="mini-label">学习条目</p>
              </div>
            </div>
            <div class="mini-card">
              <div class="mini-icon">
                <i class="fas fa-calendar"></i>
              </div>
              <div class="mini-info">
                <p class="mini-value">{{ (category.created_at && category.created_at.slice(0, 10)) || '--' }}</p>
                <p class="mini-label">创建日期</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 热门条目卡片 -->
        <div class="panel hot-items-panel" v-if="hotSubcategories && hotSubcategories.length > 0">
          <div class="panel-header">
            <h2>热门技术</h2>
            <span class="panel-label">推荐学习</span>
          </div>
          <div class="hot-items-list">
            <div
              v-for="subcat in hotSubcategories"
              :key="subcat.id"
              class="hot-item-card"
              @click="goToSubcategory(subcat.id)"
            >
              <div class="hot-item-icon">
                <img 
                  v-if="subcat.icon_image_url"
                  :src="subcat.icon_image_url" 
                  :alt="subcat.name"
                  class="hot-item-icon-image"
                />
                <div 
                  v-else
                  class="hot-item-icon-placeholder"
                >
                  {{ subcat.name.charAt(0) }}
                </div>
              </div>
              <div class="hot-item-content">
                <h4 class="hot-item-title">{{ subcat.name }}</h4>
                <p class="hot-item-desc">{{ subcat.description || '点击查看详情' }}</p>
              </div>
              <div class="hot-badge">
                <i class="fas fa-fire"></i>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <div class="panel matrix-panel">
        <div class="panel-header">
          <h2>资源矩阵</h2>
          <span class="panel-label">全部条目</span>
        </div>
        <div class="subcategory-grid">
          <div
            v-for="subcat in category.subcategories || []"
            :key="subcat.id"
            class="subcategory-card"
            @click="goToSubcategory(subcat.id)"
          >
            <div class="card-icon large">
              <img 
                v-if="subcat.icon_image_url"
                :src="subcat.icon_image_url" 
                :alt="subcat.name"
                class="card-icon-image"
              />
              <div 
                v-else
                class="card-icon-placeholder"
              >
                {{ subcat.name.charAt(0) }}
              </div>
            </div>
            <h3>{{ subcat.name }}</h3>
            <p>{{ subcat.description || '点击查看详情' }}</p>
            <div class="card-meta">
              <span><i class="fas fa-signal"></i> 热度 {{ subcat.is_hot ? '高' : '标准' }}</span>
              <span><i class="fas fa-clock"></i> 创建于 {{ (subcat.created_at && subcat.created_at.slice(0, 10)) || '--' }}</span>
            </div>
            <span class="card-link">查看课程 <i class="fas fa-arrow-right"></i></span>
          </div>
          <p v-if="!(category.subcategories || []).length" class="empty-tip">
            该分类暂未配置技术条目。
          </p>
        </div>
      </div>

    </section>
  </div>
  <div v-else class="loading-state">
    <div class="spinner"></div>
    <p>正在加载分类详情…</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getCategoryDetail } from '@/services/category';

const route = useRoute();
const router = useRouter();
const category = ref({});

// 计算热门子分类（最多显示3个）
const hotSubcategories = computed(() => {
  if (!category.value.subcategories) {
    return [];
  }
  return category.value.subcategories
    .filter(subcat => subcat.is_hot)
    .slice(0, 3);
});

const fetchCategoryDetail = async () => {
  try {
    const response = await getCategoryDetail(route.params.id);
    category.value = response.data;
  } catch (error) {
    console.error('获取分类详情失败:', error);
  }
};

const goToSubcategory = (subcategoryId) => {
  router.push(`/learningpath/${subcategoryId}`);
};

const goToAllCategories = () => {
  router.push('/allCategories');
};

const goToCommunity = () => {
  router.push('/community');
};

onMounted(fetchCategoryDetail);
</script>

<style scoped>
.category-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 面包屑导航栏与 hero section 之间的间距更小 */
.category-page > .breadcrumb {
  margin-bottom: 10px;
}

.category-page > .breadcrumb + .hero {
  margin-top: -1.5rem; /* 抵消部分 gap，使间距更紧凑 */
}

.hero {
  background: linear-gradient(135deg, #eef2ff, #eff6ff);
  border-radius: 24px;
  padding: 2rem;
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 2rem;
  align-items: center;
  box-shadow: 0 20px 40px rgba(59, 130, 246, 0.15);
}

.hero-icon {
  width: 100px;
  height: 100px;
  border-radius: 24px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
}

.hero-icon-image {
  width: 64px;
  height: 64px;
  object-fit: contain;
}

.hero-icon-placeholder {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: bold;
}

.hero-eyebrow {
  margin: 0;
  font-size: 0.85rem;
  color: #818cf8;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero h1 {
  margin: 0.3rem 0;
  font-size: 2.4rem;
  color: #0f172a;
}

.hero-subtitle {
  margin: 0;
  color: #475569;
  line-height: 1.6;
}

.hero-stats {
  display: flex;
  gap: 1.5rem;
  margin-top: 1rem;
  color: #0ea5e9;
  font-weight: 500;
  flex-wrap: wrap;
}

.hero-stats strong {
  font-size: 1.2rem;
  color: #0f172a;
  margin-right: 0.25rem;
}

.hero-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.primary-btn,
.secondary-btn {
  border: none;
  border-radius: 999px;
  padding: 0.75rem 1.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.primary-btn {
  background: #2563eb;
  color: #fff;
  box-shadow: 0 15px 25px rgba(37, 99, 235, 0.35);
}

.secondary-btn {
  background: transparent;
  border: 1px solid #94a3b8;
  color: #0f172a;
}

.details-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.8fr);
  gap: 1.5rem;
}

.sidebar-section {
  order: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  position: sticky;
  top: 90px;
  align-self: flex-start;
}

.overview-panel {
  order: 0;
}

.hot-items-panel {
  order: 1;
}

.matrix-panel {
  order: 2;
}
.panel {
  background: #fff;
  border-radius: 20px;
  padding: 1.75rem;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.15);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.panel-label {
  padding: 0.15rem 0.75rem;
  border-radius: 999px;
  background: #dbeafe;
  color: #1e40af;
  font-size: 0.75rem;
  font-weight: 600;
}

.resource-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.resource-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
}

.resource-item:hover {
  border-color: #2563eb;
  transform: translateX(4px);
  box-shadow: 0 8px 18px rgba(37, 99, 235, 0.1);
}

.resource-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #eff6ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.resource-info h3 {
  margin: 0;
  font-size: 1.1rem;
}

.resource-info p {
  margin: 0.2rem 0 0;
  color: #475569;
  font-size: 0.9rem;
}

.empty-tip {
  margin: 0;
  text-align: center;
  color: #94a3b8;
}

.mini-card-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.mini-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  border-radius: 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.mini-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: #dbeafe;
  color: #1e40af;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mini-info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.mini-value {
  margin: 0;
  font-weight: 600;
  color: #0f172a;
}

.mini-label {
  margin: 0;
  font-size: 0.85rem;
  color: #64748b;
}

/* 热门条目卡片样式 */
.hot-items-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.hot-item-card {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 1rem;
  border-radius: 14px;
  background: linear-gradient(135deg, #fff5f5 0%, #fef2f2 100%);
  border: 1px solid #fecaca;
  transition: all 0.2s;
  cursor: pointer;
  position: relative;
}

.hot-item-card:hover {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  border-color: #f87171;
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(239, 68, 68, 0.15);
}

.hot-item-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.hot-item-icon-image {
  width: 36px;
  height: 36px;
  object-fit: contain;
  border-radius: 8px;
}

.hot-item-icon-placeholder {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: bold;
}

.hot-item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
}

.hot-item-title {
  margin: 0;
  font-weight: 600;
  color: #0f172a;
  font-size: 0.95rem;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hot-item-desc {
  margin: 0;
  font-size: 0.8rem;
  color: #64748b;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hot-badge {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 0.9rem;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.subcategory-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
}

.subcategory-card {
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 1.2rem;
  transition: all 0.2s;
  cursor: pointer;
}

.subcategory-card:hover {
  transform: translateY(-4px);
  border-color: #2563eb;
  box-shadow: 0 12px 20px rgba(37, 99, 235, 0.12);
}

.subcategory-card h3 {
  margin: 0 0 0.35rem;
  font-size: 1.05rem;
}

.subcategory-card p {
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
  min-height: 40px;
}

.card-link {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin-top: 0.6rem;
  color: #2563eb;
  font-weight: 600;
}

.card-icon.large {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.card-icon-image {
  width: 48px;
  height: 48px;
  object-fit: contain;
}

.card-icon-placeholder {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.85rem;
  color: #94a3b8;
  margin-top: 0.5rem;
}

.highlight-list {
  margin-top: 1.5rem;
}

.highlight-list h3 {
  margin: 0 0 0.6rem;
  font-size: 1rem;
  color: #0f172a;
}

.highlight-list ul {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  color: #4b5563;
  font-size: 0.9rem;
}

.highlight-list li {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.loading-state {
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  color: #475569;
}

.spinner {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 3px solid #e0e7ff;
  border-top-color: #2563eb;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 面包屑导航样式 */
.breadcrumb {
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

@media (max-width: 768px) {
  .hero {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .hero-actions {
    flex-direction: row;
    justify-content: center;
  }

  .details-grid {
    grid-template-columns: 1fr;
  }
  .sidebar-section {
    position: static;
  }
  .overview-panel,
  .hot-items-panel,
  .matrix-panel {
    order: 0;
  }
}
</style>