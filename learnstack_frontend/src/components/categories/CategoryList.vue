<template>
  <div class="category-section">
    <div class="grid">
      <div
        v-for="category in categories"
        :key="category.id"
        class="category-card"
        @click="goToCategoryDetail(category.id)"
      >
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
        <div class="category-name">{{ category.name }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

defineProps({
  categories: {
    type: Array,
    required: true
  }
});

const router = useRouter();

const goToCategoryDetail = (categoryId) => {
  router.push({
    path: `/categories/${categoryId}`
  });
};
</script>

<style scoped>
.category-section {
  padding: 24px 0;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.category-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  transition: all 0.3s;
  cursor: pointer;
}

.category-card:hover {
  transform: translateY(-5px);
  border-color: #2563eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.category-icon-image {
  width: 40px;
  height: 40px;
  object-fit: contain;
  margin-bottom: 12px;
}

.category-icon-placeholder {
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
  margin-bottom: 12px;
}

.category-name {
  font-size: 1.1rem;
  font-weight: 600;
  text-align: center;
}
</style>