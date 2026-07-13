<template>
  <div class="all-categories-page">
    <div class="page-header">
      <h1>所有技术分类</h1>
      <p class="page-desc">探索热门技术领域和学习资源</p>
    </div>

    <div class="category-grid">
      <!-- 父分类卡片，添加点击跳转 -->
      <div 
        v-for="category in categories" 
        :key="category.id" 
        class="category-card"
        @click="goToCategory(category.id)"
      >
        <div class="card-header">
          <img 
            v-if="category.icon_image_url"
            :src="category.icon_image_url" 
            :alt="category.name"
            class="category-icon-image"
          />
          <div 
            v-else
            class="category-icon-placeholder"
          >
            {{ category.name.charAt(0) }}
          </div>
          <h2 class="category-title">{{ category.name }}</h2>
        </div>
        
        <!-- 子分类列表，已有跳转逻辑 -->
        <div class="subcategory-list">
          <div 
            v-for="subcat in category.subcategories" 
            :key="subcat.id" 
            class="subcategory-item"
            @click="goToSubcategory(subcat.id)"
          >
            <img 
              v-if="subcat.icon_image_url"
              :src="subcat.icon_image_url" 
              :alt="subcat.name"
              class="sub-icon-image"
            />
            <div 
              v-else
              class="sub-icon-placeholder"
            >
              {{ subcat.name.charAt(0) }}
            </div>
            <span>{{ subcat.name }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getCategories } from '@/services/category';
import { useRouter } from 'vue-router';

const router = useRouter();
const categories = ref([]);

onMounted(async () => {
  try {
    const data = await getCategories();
    const allCategories = data.filter(cat => !cat.parent);
    
    categories.value = allCategories.map(parent => ({
      ...parent,
      subcategories: data.filter(child => child.parent === parent.id)
    }));
  } catch (error) {
    console.error('加载分类失败:', error);
  }
});

// 父分类跳转
const goToCategory = (categoryId) => {
  router.push({
    path: `/categories/${categoryId}`,
    // 若使用命名路由（推荐）：
    // name: 'CategoryDetail',
    // params: { id: categoryId }
  });
};

// 子分类跳转（跳转到学习路径页面）
const goToSubcategory = (id) => {
  router.push(`/learningpath/${id}`);
};
</script>

<style scoped>
/* 样式部分保持不变 */
.all-categories-page {
  padding: 40px 8%;
  max-width: 1440px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-desc {
  color: #6b7280;
  margin-top: 10px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.category-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  transition: all 0.3s;
  overflow: hidden;
  cursor: pointer;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  border-color: #2563eb;
}

.card-header {
  padding: 20px;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
}

.category-icon-image {
  width: 28px;
  height: 28px;
  object-fit: contain;
  margin-right: 12px;
}

.category-icon-placeholder {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: bold;
  margin-right: 12px;
}

.category-title {
  font-size: 1.2rem;
  font-weight: 600;
}

.subcategory-list {
  padding: 16px;
}

.subcategory-item {
  padding: 10px 16px;
  margin-bottom: 8px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
  cursor: pointer;
}

.subcategory-item:hover {
  background: #f3f4f6;
}

.sub-icon-image {
  width: 18px;
  height: 18px;
  object-fit: contain;
  margin-right: 10px;
}

.sub-icon-placeholder {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: bold;
  margin-right: 10px;
}
</style>