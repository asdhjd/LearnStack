<template>
  <div class="dashboard-container">
    <h1 class="dashboard-title">学习数据看板</h1>
    
    <div class="stats-grid">
      <!-- 学习时长卡片 -->
      <div class="stat-card">
        <div class="stat-header">
          <h3 class="stat-title">本周学习时长</h3>
          <i class="fas fa-clock stat-icon"></i>
        </div>
        <div class="stat-value">{{ weeklyStudyTime }} 小时</div>
        <div class="stat-subtitle">每周自动刷新</div>
      </div>
      
      <!-- 累计学习时长卡片 -->
      <div class="stat-card">
        <div class="stat-header">
          <h3 class="stat-title">累计学习时长</h3>
          <i class="fas fa-hourglass-half stat-icon"></i>
        </div>
        <div class="stat-value">{{ totalStudyTime }} 小时</div>
        <div class="stat-subtitle">所有时间累计</div>
      </div>
      
      <!-- 学习进度卡片 -->
      <div class="stat-card">
        <div class="stat-header">
          <h3 class="stat-title">整体学习进度</h3>
          <i class="fas fa-chart-line stat-icon"></i>
        </div>
        <div class="progress-container">
          <div 
            class="progress-bar" 
            :style="{ width: overallProgress + '%' }"
          ></div>
        </div>
        <div class="stat-value">{{ overallProgress }}%</div>
      </div>
    </div>
    
    <!-- 学习路径进度详情 -->
    <div class="paths-section">
      <div class="section-header">
        <h2 class="section-title">学习路径进度详情</h2>

      </div>
      <div v-if="learningPaths.length > 0" class="paths-list">
        <div 
          v-for="path in learningPaths" 
          :key="path.id"
          class="path-card"
          @click="navigateToLearningPath(path.id)"
        >
          <div class="path-info">
            <div class="path-header">
              <h4 class="path-name">{{ path.name }}</h4>
              <button 
                class="delete-progress-btn"
                @click.stop="deletePathProgress(path.id, path.name)"
                title="删除此学习路径的所有进度记录"
              >
                <i class="fas fa-trash-alt"></i>
              </button>
            </div>
            <div class="path-progress">
              {{ path.completedCount }} / {{ path.totalCount }} 个阶段已完成
            </div>
          </div>
          <div class="path-bar-container">
            <div 
              class="path-progress-bar" 
              :style="{ width: path.progress + '%' }"
            ></div>
          </div>
          <div class="path-percentage">{{ path.progress }}%</div>
        </div>
      </div>
      <div v-else class="empty-state">
        <h3>暂无学习进度记录</h3>
      </div>
    </div>
    

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { getAllTechnologies } from '@/services/category';
import { getLearningPathByCategory } from '@/services/learningPathService';

defineOptions({
  name: 'UserDashboard'
});

// 学习时长数据
const weeklyStudyTime = ref(0);
const totalStudyTime = ref(0);

// 学习路径进度数据
const learningPaths = ref([]);
const router = useRouter();

// 技术分类数据 - 从后端API获取
const technologies = ref([]);
let techMap = new Map();



// 计算整体学习进度
const overallProgress = computed(() => {
  if (learningPaths.value.length === 0) return 0;
  
  // 计算所有路径的总阶段数和已完成阶段数
  const totalAllPaths = learningPaths.value.reduce((sum, path) => sum + path.totalCount, 0);
  const completedAllPaths = learningPaths.value.reduce((sum, path) => sum + path.completedCount, 0);
  
  // 计算加权平均进度，确保更准确地反映整体学习情况
  // 如果没有完成任何阶段，返回0
  if (completedAllPaths === 0) return 0;
  
  // 计算进度百分比
  const progress = Math.round((completedAllPaths / totalAllPaths) * 100);
  
  // 确保进度在0-100之间
  return Math.min(Math.max(progress, 0), 100);
});

// 存储每个学习路径的详细信息
const learningPathDetails = ref(new Map());

// 获取学习路径详情
const fetchLearningPathDetails = async (categoryId) => {
  try {
    // 如果已经获取过该路径的详情，则直接返回
    if (learningPathDetails.value.has(categoryId)) {
      return learningPathDetails.value.get(categoryId);
    }
    
    // 从API获取学习路径详情
    const response = await getLearningPathByCategory(categoryId);
    const pathDetails = response.data;
    
    // 存储学习路径详情
    learningPathDetails.value.set(categoryId, pathDetails);
    return pathDetails;
  } catch (error) {
    console.error(`获取学习路径 ${categoryId} 详情失败:`, error);
    return null;
  }
};

// 跳转到学习路径详情页
const navigateToLearningPath = (pathId) => {
  router.push(`/learningpath/${pathId}`);
};

// 获取学习路径的总阶段数 - 与LearningPathDetail.vue中相似的实现
const getStagesCount = (categoryId) => {
  // 从存储的学习路径详情中获取阶段数
  if (learningPathDetails.value.has(categoryId)) {
    const pathDetails = learningPathDetails.value.get(categoryId);
    if (pathDetails && pathDetails.stages) {
      return pathDetails.stages.length;
    }
  }
  return 0; // 默认返回0
};

// 从localStorage加载学习进度数据
const loadLearningProgress = async () => {
  try {
    // 获取所有以'user_progress_'开头的键（与LearningPathDetail.vue中使用的键名保持一致）
    const keys = Object.keys(localStorage).filter(key => key.startsWith('user_progress_'));
    const paths = [];
    
    // 为每个学习路径计算进度
    for (const key of keys) {
      const categoryId = key.replace('user_progress_', '');
      
      // 增加categoryId有效性检查，避免使用undefined或非数字ID
      if (!categoryId || categoryId === 'undefined' || isNaN(Number(categoryId))) {
        console.warn(`跳过无效的categoryId: ${categoryId}`);
        continue;
      }
      
      const userProgressJSON = localStorage.getItem(key);
      
      if (userProgressJSON) {
        try {
          const userProgress = JSON.parse(userProgressJSON);
          
          // 确保userProgress是数组格式
          if (!Array.isArray(userProgress)) {
            console.warn(`学习进度数据不是有效数组 (${key})`);
            continue;
          }
          
          // 计算已完成的阶段数（过滤出is_completed为true的条目）
          const completedStages = userProgress.filter(progress => progress.is_completed);
          const completedCount = completedStages.length;
          
          // 只显示有实际完成记录的学习路径
          if (completedCount > 0) {
            // 获取真实的学习路径名称
            const pathName = getTechnologyName(categoryId);
            
            // 尝试获取学习路径详情以获取真实阶段数
            try {
              await fetchLearningPathDetails(categoryId);
            } catch (fetchError) {
              console.warn(`获取学习路径 ${categoryId} 详情失败，使用备用阶段数计算:`, fetchError);
            }
            
            // 使用getStagesCount函数获取总阶段数
            let totalCount = getStagesCount(categoryId);
            
            // 如果无法获取真实阶段数，使用备用计算方式
            if (totalCount === 0) {
              // 尝试从userProgress中获取唯一阶段数作为备选
              const uniqueStageIds = new Set(userProgress.map(p => p.stage_id).filter(id => id));
              totalCount = Math.max(uniqueStageIds.size, completedCount + 5, 10);
            }
            
            const progress = Math.round((completedCount / totalCount) * 100);
            
            paths.push({
              id: categoryId,
              name: pathName,
              totalCount,
              completedCount,
              progress
            });
          }
        } catch (parseError) {
          console.error(`解析学习进度数据失败 (${key}):`, parseError);
        }
      }
    }
    
    learningPaths.value = paths;
  } catch (error) {
    console.error('加载学习进度失败:', error);
  }
};

// 获取技术名称 - 从后端获取的技术分类数据中查找
const getTechnologyName = (categoryId) => {
  if (!categoryId || categoryId === 'undefined') return '未知技术';
  
  // 从技术映射中查找
  const tech = techMap.get(categoryId);
  return tech || `学习路径 ${categoryId}`;
};

// 删除特定学习路径进度 - 直接删除，无需确认
const deletePathProgress = (pathId, pathName) => {
  try {
    // 使用与LearningPathDetail.vue相同的键名
    const key = `user_progress_${pathId}`;
    localStorage.removeItem(key);
    
    // 重新加载学习进度数据
    loadLearningProgress();
    
    // 显示删除成功提示
    alert(`"${pathName}"的学习进度已成功删除！`);
  } catch (error) {
    console.error('删除学习进度失败:', error);
    alert('删除学习进度失败，请稍后再试。');
  }
};



// 获取技术分类数据
const fetchTechnologies = async () => {
  try {
    const response = await getAllTechnologies();
    technologies.value = response;
    
    // 创建ID到技术名称的映射，用于快速查找
    techMap = new Map();
    technologies.value.forEach(tech => {
      techMap.set(String(tech.id), tech.name);
    });
    
    // 获取技术分类数据后重新加载学习进度，确保显示正确的技术名称
    loadLearningProgress();
  } catch (error) {
    console.error('获取技术分类数据失败:', error);
  }
};

// 加载学习时长数据
const loadStudyTimeData = async () => {
  try {
    // 优先从后端获取学习时长数据
    try {
      const { getStudyTimeStats } = await import('@/services/learningPathService');
      const response = await getStudyTimeStats();
      if (response.data) {
        weeklyStudyTime.value = response.data.weekly_study_time || 0;
        totalStudyTime.value = response.data.total_study_time || 0;
        console.log('从后端获取学习时长数据:', response.data);
        return;
      }
    } catch (apiError) {
      console.warn('从后端获取学习时长失败，尝试从localStorage加载:', apiError);
      // 如果后端API失败，尝试从localStorage加载（作为降级方案）
    }
    
    // 降级方案：从localStorage加载
    const weeklyTime = localStorage.getItem('weeklyStudyTime');
    const totalTime = localStorage.getItem('totalStudyTime');
    weeklyStudyTime.value = weeklyTime ? parseFloat(weeklyTime) : 0;
    totalStudyTime.value = totalTime ? parseFloat(totalTime) : 0;
  } catch (error) {
    console.error('加载学习时长数据失败:', error);
  }
};

// 初始化页面数据
onMounted(async () => {
  // 先获取技术分类数据，然后再加载学习进度
  await fetchTechnologies();
  await loadLearningProgress(); // 修改为异步调用
  await loadStudyTimeData();
});
</script>

<style scoped>
.dashboard-container {
  padding: 40px 8%;
  max-width: 1440px;
  margin: 0 auto;
}

.dashboard-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 40px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 60px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.stat-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #6b7280;
  margin: 0;
}

.stat-icon {
  font-size: 1.5rem;
  color: #2563eb;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.stat-subtitle {
  font-size: 0.9rem;
  color: #9ca3af;
}

/* 进度条样式 */
.progress-container {
  height: 12px;
  background-color: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #2563eb, #3b82f6);
  border-radius: 6px;
  transition: width 0.3s ease;
}

/* 学习路径部分 */
.paths-section {
  margin-bottom: 60px;
}

.section-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}



.paths-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.path-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto auto;
  gap: 12px;
  align-items: center;
}

.path-info {
  grid-column: 1;
}

.path-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.delete-progress-btn {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: all 0.2s ease;
  font-size: 1rem;
}

.delete-progress-btn:hover {
  background-color: #fef2f2;
  color: #dc2626;
  transform: scale(1.1);
}

.path-name {
  font-size: 1.2rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 8px 0;
}

.path-progress {
  font-size: 0.9rem;
  color: #6b7280;
}

.path-bar-container {
  grid-column: 1;
  height: 8px;
  background-color: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.path-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #34d399);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.path-percentage {
  grid-column: 2;
  grid-row: 1 / 3;
  font-size: 1.5rem;
  font-weight: 700;
  color: #10b981;
}

.empty-state {
  background: #f9fafb;
  border-radius: 12px;
  padding: 60px 48px;
  text-align: center;
  color: #6b7280;
  border: 2px dashed #e5e7eb;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 20px 16px;
  }
  
  .dashboard-title {
    font-size: 2rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 24px;
  }
  
  .path-card {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .path-percentage {
    grid-column: 1;
    grid-row: auto;
    align-self: flex-end;
  }
  

}
</style>