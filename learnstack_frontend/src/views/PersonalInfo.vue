<template>
  <div class="personal-info-wrapper">
    <div class="personal-info-container">
      <h1 class="page-title">用户中心</h1>
      
      <!-- 标签页导航 -->
      <div class="tabs-nav">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          :class="['tab-btn', { active: activeTab === tab.key }]"
          @click="activeTab = tab.key"
        >
          <i :class="tab.icon"></i>
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <!-- 标签页内容 -->
      <div class="tabs-content">
        <!-- 个人信息标签页 -->
        <PersonalInfoTab v-show="activeTab === 'info'" />

        <!-- 我的收藏标签页 -->
        <FavoritesTab v-show="activeTab === 'favorites'" />

        <!-- 数据看板标签页 -->
        <DashboardTab v-show="activeTab === 'dashboard'" />
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue';
import PersonalInfoTab from '@/components/user/PersonalInfoTab.vue';
import FavoritesTab from '@/components/user/FavoritesTab.vue';
import DashboardTab from '@/components/user/DashboardTab.vue';

// 标签页相关
const activeTab = ref('info');
const tabs = [
  { key: 'info', label: '个人信息', icon: 'fas fa-user' },
  { key: 'favorites', label: '我的收藏', icon: 'fas fa-heart' },
  { key: 'dashboard', label: '数据看板', icon: 'fas fa-chart-bar' }
];
</script>
<style scoped>
.personal-info-wrapper {
  min-height: calc(100vh - 80px);
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 40px 20px;
}

.personal-info-container {
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  font-size: 2rem;
  color: #111827;
  text-align: center;
  font-weight: 600;
}

/* 标签页导航 */
.tabs-nav {
  display: flex;
  gap: 12px;
  margin-bottom: 32px;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0;
}

.tab-btn {
  padding: 12px 24px;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  color: #6b7280;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: -2px;
}

.tab-btn:hover {
  color: #2563eb;
  background: rgba(37, 99, 235, 0.05);
}

.tab-btn.active {
  color: #2563eb;
  border-bottom-color: #2563eb;
  background: rgba(37, 99, 235, 0.05);
}

.tab-btn i {
  font-size: 1.1rem;
}

.tabs-content {
  min-height: 400px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .personal-info-wrapper {
    padding: 20px 16px;
  }
  
  .page-title {
    font-size: 1.5rem;
    margin-bottom: 24px;
  }
  
  .tabs-nav {
    flex-wrap: wrap;
  }
  
  .tab-btn {
    flex: 1;
    min-width: 120px;
    justify-content: center;
  }
}
</style>