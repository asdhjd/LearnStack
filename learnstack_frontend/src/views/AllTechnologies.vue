<template>
  <div class="all-technologies-page">
    <div class="page-header">
      <h1 class="page-title">所有技术</h1>
    </div>

    <div class="technology-grid">
      <div
        v-for="tech in technologies"
        :key="tech.id"
        class="technology-card"
        :style="{ borderColor: tech.is_hot ? '#2563eb' : '#e5e7eb' }"
        @click="goToTechnology(tech.id)"
        style="cursor: pointer;"
      >
        <div class="card-top">
          <img 
            v-if="tech.icon_image_url"
            :src="tech.icon_image_url" 
            :alt="tech.name"
            class="tech-icon-image"
          />
          <div 
            v-else
            class="tech-icon-placeholder"
          >
            {{ tech.name.charAt(0) }}
          </div>
          <div class="status-badge" v-if="tech.is_hot">热门</div>
        </div>
        <h3 class="tech-name">{{ tech.name }}</h3>
        <p class="tech-desc">{{ tech.description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getAllTechnologies } from '@/services/category';

// 状态管理
const technologies = ref([]);
const router = useRouter();

// 生命周期：加载数据
const loadTechnologies = async () => {
  try {
    const data = await getAllTechnologies();
    technologies.value = data;
  } catch (error) {
    console.error('加载技术数据失败:', error);
  }
};

// 跳转到技术详情页
const goToTechnology = (techId) => {
  router.push(`/learningpath/${techId}`);
};

onMounted(loadTechnologies);
</script>

<style scoped>
.all-technologies-page {
  padding: 40px 8%;
  max-width: 1440px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.page-title {
  font-size: 2.2rem;
  font-weight: 700;
  color: #111827;
}



.technology-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.technology-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
  min-height: 240px;
}

.technology-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.tech-icon-image {
  width: 48px;
  height: 48px;
  object-fit: contain;
}

.tech-icon-placeholder {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: bold;
}

.status-badge {
  padding: 4px 8px;
  background: #2563eb;
  color: white;
  font-size: 0.8rem;
  border-radius: 4px;
}

.tech-name {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: #2563eb;
}

.tech-desc {
  font-size: 0.95rem;
  color: #6b7280;
  line-height: 1.5;
}
</style>