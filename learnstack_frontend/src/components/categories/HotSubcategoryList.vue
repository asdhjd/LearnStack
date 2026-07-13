<template>
  <div class="hot-section">
    <div class="grid">
      <div
        v-for="subcat in subcategories"
        :key="subcat.id"
        class="subcategory-card"
        @click="handleClick(subcat)"
      >
        <img 
          v-if="subcat.icon_image_url"
          :src="subcat.icon_image_url" 
          :alt="subcat.name"
          class="subcategory-icon-image"
        />
        <div 
          v-else
          class="subcategory-icon-placeholder"
        >
          {{ subcat.name.charAt(0) }}
        </div>
        <div class="subcategory-name">{{ subcat.name }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getHotSubcategories } from '@/services/category';

const router = useRouter();
const subcategories = ref([]);

onMounted(async () => {
  try {
    const response = await getHotSubcategories();
    subcategories.value = response.data;
  } catch (error) {
    console.error('加载热门子分类失败:', error);
  }
});

const handleClick = (subcat) => {
  router.push(`/learningpath/${subcat.id}`);
};
</script>

<style scoped>
.hot-section {
  padding: 24px 0;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.subcategory-card {
  padding: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s;
  background-color: white;
}

.subcategory-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: #2563eb;
}

.subcategory-icon-image {
  width: 40px;
  height: 40px;
  object-fit: contain;
  margin-bottom: 10px;
}

.subcategory-icon-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0 auto 10px;
}

.subcategory-name {
  font-size: 1.1rem;
  font-weight: 500;
  color: #111827;
}
</style>