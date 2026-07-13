<template>
  <div class="tab-panel">
    <div class="dashboard-content">
      <h2 class="section-title">学习数据看板</h2>
      
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-header">
            <h3 class="stat-title">本周学习时长</h3>
            <i class="fas fa-clock stat-icon"></i>
          </div>
          <div class="stat-value">{{ weeklyStudyTime }} 小时</div>
          <div class="stat-subtitle">每周自动刷新</div>
        </div>
        
        <div class="stat-card">
          <div class="stat-header">
            <h3 class="stat-title">累计学习时长</h3>
            <i class="fas fa-hourglass-half stat-icon"></i>
          </div>
          <div class="stat-value">{{ totalStudyTime }} 小时</div>
          <div class="stat-subtitle">所有时间累计</div>
        </div>
        
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

      <div class="charts-section">
        <div class="chart-card donut-card">
          <div class="chart-header">
            <h3>整体学习完成度</h3>
            <p>基于所有学习路径实时计算</p>
          </div>
          <div class="donut-wrapper">
            <svg viewBox="0 0 140 140" class="donut-chart">
              <circle class="donut-track" cx="70" cy="70" r="60"></circle>
              <circle 
                class="donut-value" 
                cx="70" 
                cy="70" 
                r="60"
                :stroke-dasharray="donutCircumference"
                :stroke-dashoffset="donutOffset"
              ></circle>
              <text x="70" y="70" text-anchor="middle" class="donut-label">
                {{ overallProgress }}%
              </text>
              <text x="70" y="90" text-anchor="middle" class="donut-sub-label">
                完成率
              </text>
            </svg>
            <div class="donut-legend">
              <div class="legend-item">
                <span class="legend-dot completed"></span>
                已完成阶段
                <strong>{{ completedTotal }}</strong>
              </div>
              <div class="legend-item">
                <span class="legend-dot remaining"></span>
                剩余阶段
                <strong>{{ remainingTotal }}</strong>
              </div>
            </div>
          </div>
        </div>

        <div class="chart-card bar-card">
          <div class="chart-header">
            <h3>学习路径进度</h3>
            <p>展示进度最高的路径</p>
          </div>
          <div v-if="topPaths.length" class="bar-list">
            <div 
              v-for="path in topPaths" 
              :key="path.id" 
              class="bar-item"
            >
              <div class="bar-label">
                <span class="path-name">{{ path.name }}</span>
                <span class="path-progress-text">{{ path.completedCount }}/{{ path.totalCount }} 阶段</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: path.progress + '%' }"></div>
              </div>
              <div class="bar-value">{{ path.progress }}%</div>
            </div>
          </div>
          <div v-else class="empty-chart">
            <p>暂无学习路径数据</p>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { getAllTechnologies } from '@/services/category';
import { getLearningPathByCategory, getStudyTimeStats } from '@/services/learningPathService';

const weeklyStudyTime = ref(0);
const totalStudyTime = ref(0);
const learningPaths = ref([]);
const technologies = ref([]);
let techMap = new Map();
const learningPathDetails = ref(new Map());

const donutRadius = 60;
const donutCircumference = 2 * Math.PI * donutRadius;

const overallProgress = computed(() => {
  if (learningPaths.value.length === 0) return 0;
  const totalAllPaths = learningPaths.value.reduce((sum, path) => sum + path.totalCount, 0);
  const completedAllPaths = learningPaths.value.reduce((sum, path) => sum + path.completedCount, 0);
  if (completedAllPaths === 0) return 0;
  const progress = Math.round((completedAllPaths / totalAllPaths) * 100);
  return Math.min(Math.max(progress, 0), 100);
});

const donutOffset = computed(() => {
  return donutCircumference * (1 - overallProgress.value / 100);
});

const completedTotal = computed(() => {
  return learningPaths.value.reduce((sum, path) => sum + path.completedCount, 0);
});

const remainingTotal = computed(() => {
  return learningPaths.value.reduce((sum, path) => sum + Math.max(path.totalCount - path.completedCount, 0), 0);
});

const topPaths = computed(() => {
  if (!learningPaths.value.length) return [];
  return [...learningPaths.value]
    .sort((a, b) => b.progress - a.progress)
    .slice(0, 4);
});

const fetchLearningPathDetails = async (categoryId) => {
  try {
    if (learningPathDetails.value.has(categoryId)) {
      return learningPathDetails.value.get(categoryId);
    }
    const response = await getLearningPathByCategory(categoryId);
    const pathDetails = response.data;
    learningPathDetails.value.set(categoryId, pathDetails);
    return pathDetails;
  } catch (error) {
    console.error(`获取学习路径 ${categoryId} 详情失败:`, error);
    return null;
  }
};

const getStagesCount = (categoryId) => {
  if (learningPathDetails.value.has(categoryId)) {
    const pathDetails = learningPathDetails.value.get(categoryId);
    if (pathDetails && pathDetails.stages) {
      return pathDetails.stages.length;
    }
  }
  return 0;
};

const loadLearningProgress = async () => {
  try {
    const keys = Object.keys(localStorage).filter(key => key.startsWith('user_progress_'));
    const paths = [];
    for (const key of keys) {
      const categoryId = key.replace('user_progress_', '');
      if (!categoryId || categoryId === 'undefined' || isNaN(Number(categoryId))) {
        continue;
      }
      const userProgressJSON = localStorage.getItem(key);
      if (userProgressJSON) {
        try {
          const userProgress = JSON.parse(userProgressJSON);
          if (!Array.isArray(userProgress)) {
            continue;
          }
          const completedStages = userProgress.filter(progress => progress.is_completed);
          const completedCount = completedStages.length;
          if (completedCount > 0) {
            const pathName = getTechnologyName(categoryId);
            try {
              await fetchLearningPathDetails(categoryId);
            } catch (fetchError) {
              console.warn(`获取学习路径 ${categoryId} 详情失败:`, fetchError);
            }
            let totalCount = getStagesCount(categoryId);
            if (totalCount === 0) {
              const uniqueStageIds = new Set(userProgress.map(p => p.stage_id).filter(id => id));
              totalCount = uniqueStageIds.size || completedCount || 1;
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

const getTechnologyName = (categoryId) => {
  if (!categoryId || categoryId === 'undefined') return '未知技术';
  const tech = techMap.get(categoryId);
  return tech || `学习路径 ${categoryId}`;
};

const fetchTechnologies = async () => {
  try {
    const response = await getAllTechnologies();
    technologies.value = response;
    techMap = new Map();
    technologies.value.forEach(tech => {
      techMap.set(String(tech.id), tech.name);
    });
    await loadLearningProgress();
  } catch (error) {
    console.error('获取技术分类数据失败:', error);
  }
};

const loadStudyTimeData = async () => {
  try {
    // 优先从后端获取学习时长数据
    try {
      const data = await getStudyTimeStats();
      console.log('[DashboardTab] 学习时长统计API返回数据:', data);
      
      // 后端API直接返回数据对象（getStudyTimeStats已经处理了response.data）
      if (data && typeof data === 'object') {
        const weekly = parseFloat(data.weekly_study_time || 0);
        const total = parseFloat(data.total_study_time || 0);
        
        // 只有当数据发生变化时才更新，避免不必要的响应式更新
        if (weekly !== weeklyStudyTime.value || total !== totalStudyTime.value) {
          weeklyStudyTime.value = weekly;
          totalStudyTime.value = total;
          console.log('[DashboardTab] 学习时长数据已更新:', {
            weekly: weeklyStudyTime.value,
            total: totalStudyTime.value,
            weeklyRaw: data.weekly_study_time,
            totalRaw: data.total_study_time
          });
        } else {
          console.log('[DashboardTab] 学习时长数据无变化:', {
            weekly: weeklyStudyTime.value,
            total: totalStudyTime.value
          });
        }
        return;
      } else {
        console.warn('[DashboardTab] API返回数据格式异常:', data);
      }
    } catch (apiError) {
      console.warn('[DashboardTab] 从后端获取学习时长失败，尝试从localStorage加载:', apiError);
      // 如果后端API失败，尝试从localStorage加载（作为降级方案）
    }
    
    // 降级方案：从localStorage加载
    const weeklyTime = localStorage.getItem('weeklyStudyTime');
    const totalTime = localStorage.getItem('totalStudyTime');
    weeklyStudyTime.value = weeklyTime ? parseFloat(weeklyTime) : 0;
    totalStudyTime.value = totalTime ? parseFloat(totalTime) : 0;
    console.log('[DashboardTab] 从localStorage加载学习时长:', {
      weekly: weeklyStudyTime.value,
      total: totalStudyTime.value
    });
  } catch (error) {
    console.error('[DashboardTab] 加载学习时长数据失败:', error);
  }
};

// 定时刷新学习时长数据
let studyTimeRefreshTimer = null;

onMounted(async () => {
  await fetchTechnologies();
  await loadLearningProgress();
  await loadStudyTimeData();
  
  // 每10秒刷新一次学习时长数据（缩短刷新间隔以便更快看到变化）
  studyTimeRefreshTimer = setInterval(() => {
    loadStudyTimeData();
  }, 10 * 1000);
});

// 组件卸载时清理定时器
onBeforeUnmount(() => {
  if (studyTimeRefreshTimer) {
    clearInterval(studyTimeRefreshTimer);
    studyTimeRefreshTimer = null;
  }
});
</script>

<style scoped>
.tab-panel {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dashboard-content {
  background: #ffffff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.section-title {
  font-size: 1.5rem;
  color: #111827;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e5e7eb;
  font-weight: 600;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 60px;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 60px;
}

.chart-card {
  background: #f9fafb;
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.chart-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #0f172a;
  font-weight: 600;
}

.chart-header p {
  margin: 6px 0 20px;
  color: #64748b;
  font-size: 0.9rem;
}

.donut-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.donut-chart {
  width: 220px;
  height: 220px;
}

.donut-track {
  fill: none;
  stroke: #e5e7eb;
  stroke-width: 12;
}

.donut-value {
  fill: none;
  stroke: url(#donutGradient);
  stroke: #2563eb;
  stroke-width: 12;
  stroke-linecap: round;
  transform: rotate(-90deg);
  transform-origin: 70px 70px;
  transition: stroke-dashoffset 0.4s ease;
}

.donut-label {
  fill: #0f172a;
  font-size: 1.6rem;
  font-weight: 700;
}

.donut-sub-label {
  fill: #94a3b8;
  font-size: 0.9rem;
}

.donut-legend {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  justify-content: center;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #475569;
}

.legend-item strong {
  color: #0f172a;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.legend-dot.completed {
  background: #2563eb;
}

.legend-dot.remaining {
  background: #e2e8f0;
}

.bar-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.bar-item {
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.05);
}

.bar-label {
  display: flex;
  justify-content: space-between;
  color: #0f172a;
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 8px;
}

.path-progress-text {
  color: #94a3b8;
  font-weight: 500;
  font-size: 0.85rem;
}

.bar-track {
  position: relative;
  height: 10px;
  border-radius: 999px;
  background: #e2e8f0;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #22d3ee, #2563eb);
  transition: width 0.3s ease;
}

.bar-value {
  margin-top: 6px;
  text-align: right;
  font-size: 0.85rem;
  color: #475569;
  font-weight: 600;
}

.empty-chart {
  text-align: center;
  color: #94a3b8;
  padding: 1rem 0;
}

.stat-card {
  background: #f9fafb;
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

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 24px;
  }
  
}
</style>