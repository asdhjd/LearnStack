<template>
  <div class="admin-dashboard">
    <AdminSidebar />
    
    <div class="admin-content">
      <header class="admin-header">
        <h1>数据统计仪表盘</h1>
      </header>



      <!-- 错误状态 -->
        <div v-if="error" class="error-message">
          <p>{{ error }}</p>
          <button @click="fetchData" class="retry-btn">重试</button>
        </div>
        
        <!-- 数据展示 -->
        <div v-else class="stats-container">
        <!-- 用户统计 -->
        <section class="stats-section">
          <h2 class="section-title">用户统计</h2>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon user-icon">👤</div>
              <div class="stat-info">
                <h3>{{ (stats.user_stats && stats.user_stats.total_users) || 0 }}</h3>
                <p>总用户数</p>
              </div>
            </div>

            <div class="stat-card">
              <div class="stat-icon today-icon">📅</div>
              <div class="stat-info">
                <h3>{{ (stats.user_stats && stats.user_stats.new_users_today) || 0 }}</h3>
                <p>今日新增</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon week-icon">📊</div>
              <div class="stat-info">
                <h3>{{ (stats.user_stats && stats.user_stats.new_users_this_week) || 0 }}</h3>
                <p>本周新增</p>
              </div>
            </div>

          </div>
          <!-- 用户增长趋势图 -->
          <div class="chart-card">
            <h3 class="chart-title">用户与帖子增长趋势（过去7天）</h3>
            <div class="chart-wrapper">
              <canvas ref="userGrowthChart"></canvas>
            </div>
          </div>
        </section>

        <!-- 社区互动统计 -->
        <section class="stats-section">
          <h2 class="section-title">社区互动统计</h2>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon question-icon">❓</div>
              <div class="stat-info">
                <h3>{{ (stats.community_stats && stats.community_stats.total_questions) || 0 }}</h3>
                <p>总帖子数</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon answer-icon">💬</div>
              <div class="stat-info">
                <h3>{{ (stats.community_stats && stats.community_stats.total_answers) || 0 }}</h3>
                <p>总回答数</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon view-icon">👁️</div>
              <div class="stat-info">
                <h3>{{ (stats.community_stats && stats.community_stats.total_views) || 0 }}</h3>
                <p>总浏览量</p>
              </div>
            </div>
          </div>
        </section>

        <!-- 资源统计 -->
        <section class="stats-section">
          <h2 class="section-title">资源统计</h2>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon resource-icon">📚</div>
              <div class="stat-info">
                <h3>{{ (stats.resource_stats && stats.resource_stats.total_resources) || 0 }}</h3>
                <p>总资源数</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon approved-icon">✅</div>
              <div class="stat-info">
                <h3>{{ (stats.resource_stats && stats.resource_stats.approved_resources) || 0 }}</h3>
                <p>已审核通过</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon pending-icon">⏳</div>
              <div class="stat-info">
                <h3>{{ (stats.resource_stats && stats.resource_stats.pending_resources) || 0 }}</h3>
                <p>待审核</p>
              </div>
            </div>
          </div>
          <!-- 资源统计图表 -->
          <div class="resource-charts-container">
            <!-- 资源类型饼图 -->
            <div class="chart-card">
              <h3 class="chart-title">资源类型分布</h3>
              <div class="chart-wrapper">
                <canvas ref="resourceTypeChart"></canvas>
              </div>
            </div>
            <!-- 资源数据统计柱状图 -->
            <div class="chart-card">
              <h3 class="chart-title">资源数据统计</h3>
              <div class="chart-wrapper">
                <canvas ref="resourceStatusChart"></canvas>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import AdminSidebar from '@/components/admin/AdminSidebar.vue';
import axios from 'axios';
import { API_BASE_URL } from '@/config/api';
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  LineController,
  BarController,
  DoughnutController,
  Filler
} from 'chart.js';

// 注册 Chart.js 组件
Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  LineController,
  BarController,
  DoughnutController,
  Filler
);

const error = ref(null);
const stats = ref({});
const userGrowthChart = ref(null);
const resourceStatusChart = ref(null);
const resourceTypeChart = ref(null);

let userGrowthChartInstance = null;
let resourceStatusChartInstance = null;
let resourceTypeChartInstance = null;

const API_URL = `${API_BASE_URL}/users`;

// 获取统计数据
const fetchData = async () => {
  error.value = null;
  
  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.get(`${API_URL}/admin/dashboard/stats/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    stats.value = response.data;
    await nextTick();
    initCharts();
  } catch (err) {
    console.error('获取统计数据失败:', err);
    error.value = err.response?.data?.error || '获取统计数据失败，请稍后再试';
  }
};

// 生成过去7天的日期标签
const getLast7Days = () => {
  const days = [];
  for (let i = 6; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    days.push(`${month}/${day}`);
  }
  return days;
};

// 初始化图表
const initCharts = async () => {
  // 销毁旧图表
  if (userGrowthChartInstance) {
    userGrowthChartInstance.destroy();
    userGrowthChartInstance = null;
  }
  if (resourceStatusChartInstance) {
    resourceStatusChartInstance.destroy();
    resourceStatusChartInstance = null;
  }
  if (resourceTypeChartInstance) {
    resourceTypeChartInstance.destroy();
    resourceTypeChartInstance = null;
  }

  // 用户与帖子增长趋势折线图
  if (userGrowthChart.value) {
    const ctx = userGrowthChart.value.getContext('2d');
    const labels = getLast7Days();
    
    // 获取真实的7天历史数据，如果没有则使用当前总数作为所有天的值
    const userDailyStats = stats.value.user_stats?.daily_stats || null;
    const questionDailyStats = stats.value.community_stats?.daily_stats || null;
    const totalUsers = stats.value.user_stats?.total_users || 0;
    const totalQuestions = stats.value.community_stats?.total_questions || 0;
    
    let userData = [];
    let questionData = [];
    
    // 处理用户数据
    if (userDailyStats) {
      if (Array.isArray(userDailyStats)) {
        // 数组格式
        const sortedUserStats = userDailyStats.sort((a, b) => new Date(a.date) - new Date(b.date));
        userData = sortedUserStats.slice(-7).map(item => item.count || item.users || 0);
        // 如果数据不足7天，用最后一个值填充
        while (userData.length < 7) {
          userData.unshift(userData[0] || 0);
        }
      } else if (typeof userDailyStats === 'object') {
        // 对象格式，按日期顺序提取
        const dates = getLast7Days();
        userData = dates.map(date => {
          const dateKey = Object.keys(userDailyStats).find(key => {
            const statDate = new Date(key);
            const targetDate = new Date();
            targetDate.setDate(targetDate.getDate() - (6 - dates.indexOf(date)));
            return statDate.toDateString() === targetDate.toDateString();
          });
          return dateKey ? (userDailyStats[dateKey].count || userDailyStats[dateKey].users || userDailyStats[dateKey] || 0) : 0;
        });
      }
    } else {
      // 没有历史数据，使用当前总数作为所有天的值
      userData = Array(7).fill(totalUsers);
    }
    
    // 处理帖子数据
    if (questionDailyStats) {
      if (Array.isArray(questionDailyStats)) {
        // 数组格式
        const sortedQuestionStats = questionDailyStats.sort((a, b) => new Date(a.date) - new Date(b.date));
        questionData = sortedQuestionStats.slice(-7).map(item => item.count || item.questions || 0);
        // 如果数据不足7天，用最后一个值填充
        while (questionData.length < 7) {
          questionData.unshift(questionData[0] || 0);
        }
      } else if (typeof questionDailyStats === 'object') {
        // 对象格式，按日期顺序提取
        const dates = getLast7Days();
        questionData = dates.map(date => {
          const dateKey = Object.keys(questionDailyStats).find(key => {
            const statDate = new Date(key);
            const targetDate = new Date();
            targetDate.setDate(targetDate.getDate() - (6 - dates.indexOf(date)));
            return statDate.toDateString() === targetDate.toDateString();
          });
          return dateKey ? (questionDailyStats[dateKey].count || questionDailyStats[dateKey].questions || questionDailyStats[dateKey] || 0) : 0;
        });
      }
    } else {
      // 没有历史数据，使用当前总数作为所有天的值
      questionData = Array(7).fill(totalQuestions);
    }

    // 确保数据长度为7
    if (userData.length === 0) {
      userData = Array(7).fill(0);
    }
    if (questionData.length === 0) {
      questionData = Array(7).fill(0);
    }

    // 计算数据的最大值，用于设置y轴范围
    const maxValue = Math.max(...userData, ...questionData, 1);
    // 设置y轴最大值为数据最大值加上20%的缓冲，至少增加10个单位
    const yAxisMax = Math.max(maxValue * 1.2, maxValue + 10);

    userGrowthChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: '用户总数',
            data: userData,
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4,
            fill: true,
            pointRadius: 5,
            pointHoverRadius: 7
          },
          {
            label: '帖子总数',
            data: questionData,
            borderColor: 'rgb(16, 185, 129)',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.4,
            fill: true,
            pointRadius: 5,
            pointHoverRadius: 7
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top'
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            suggestedMax: yAxisMax,
            ticks: {
              stepSize: 1
            }
          }
        }
      }
    });
  }

  // 资源类型分布饼图
  if (resourceTypeChart.value) {
    const ctx = resourceTypeChart.value.getContext('2d');

    const typeLabels = {
      book: '书籍',
      course: '课程',
      article: '文章',
      project: '项目',
      tool: '工具',
      document: '文档'
    };

    // 尝试从多个可能的字段获取资源类型统计数据
    // 检查API返回的完整数据结构
    console.log('资源统计数据:', JSON.parse(JSON.stringify(stats.value.resource_stats)));
    console.log('完整stats数据:', JSON.parse(JSON.stringify(stats.value)));
    
    let resourceTypeStats = null;
    
    // 尝试不同的字段名
    if (stats.value.resource_stats?.resource_type_stats) {
      resourceTypeStats = stats.value.resource_stats.resource_type_stats;
    } else if (stats.value.resource_stats?.type_stats) {
      resourceTypeStats = stats.value.resource_stats.type_stats;
    } else if (stats.value.resource_stats?.by_type) {
      resourceTypeStats = stats.value.resource_stats.by_type;
    } else if (stats.value.resource_type_stats) {
      resourceTypeStats = stats.value.resource_type_stats;
    }
    
    // 如果API没有返回资源类型统计，主动获取
    if (!resourceTypeStats || Object.keys(resourceTypeStats).length === 0) {
      console.log('API未返回资源类型统计，开始从资源列表获取...');
      try {
        const token = localStorage.getItem('access_token');
        const typeStats = {};
        let nextUrl = `${API_BASE_URL}/resources/`;
        
        // 处理分页，获取所有资源
        while (nextUrl) {
          const response = await axios.get(nextUrl, {
            headers: {
              'Authorization': `Bearer ${token}`
            },
            params: {
              page_size: 100 // 每页100条
            }
          });
          
          const resources = response.data.results || response.data || [];
          
          // 统计资源类型
          resources.forEach(resource => {
            const type = resource.resource_type || 'unknown';
            typeStats[type] = (typeStats[type] || 0) + 1;
          });
          
          // 检查是否有下一页
          nextUrl = response.data.next || null;
        }
        
        if (Object.keys(typeStats).length > 0) {
          resourceTypeStats = typeStats;
          console.log('成功获取资源类型统计:', resourceTypeStats);
        }
      } catch (err) {
        console.error('获取资源类型统计失败:', err);
      }
    }
    
    let labels = [];
    let data = [];
    let colors = [];
    
    // 检查数据是否存在且有效
    if (resourceTypeStats && typeof resourceTypeStats === 'object' && Object.keys(resourceTypeStats).length > 0) {
      // 过滤掉值为0或null的项
      const filteredStats = Object.entries(resourceTypeStats).filter(([key, value]) => value > 0);
      
      if (filteredStats.length > 0) {
        labels = filteredStats.map(([key]) => typeLabels[key] || key);
        data = filteredStats.map(([, value]) => value);
        colors = [
          'rgba(59, 130, 246, 0.8)',   // 书籍 - 蓝色
          'rgba(16, 185, 129, 0.8)',   // 课程 - 绿色
          'rgba(139, 92, 246, 0.8)',   // 文章 - 紫色
          'rgba(245, 158, 11, 0.8)',  // 项目 - 橙色
          'rgba(236, 72, 153, 0.8)',  // 工具 - 粉色
          'rgba(34, 197, 94, 0.8)'    // 文档 - 浅绿色
        ].slice(0, labels.length);
      } else {
        // 所有值都是0，显示暂无数据
        labels = ['暂无数据'];
        data = [1];
        colors = ['rgba(148, 163, 184, 0.5)']; // 灰色
      }
    } else {
      // 没有数据时，显示一个占位项
      console.warn('未找到资源类型统计数据，请检查API返回的数据结构');
      labels = ['暂无数据'];
      data = [1];
      colors = ['rgba(148, 163, 184, 0.5)']; // 灰色
    }

    resourceTypeChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: colors,
          borderColor: '#fff',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'bottom'
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const label = context.label || '';
                const value = context.parsed || 0;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                return `${label}: ${value} (${percentage}%)`;
              }
            }
          }
        }
      }
    });
  }

  // 资源数据统计柱状图
  if (resourceStatusChart.value) {
    const ctx = resourceStatusChart.value.getContext('2d');
    const total = stats.value.resource_stats?.total_resources || 0;
    const approved = stats.value.resource_stats?.approved_resources || 0;
    const pending = stats.value.resource_stats?.pending_resources || 0;
    const newResourcesThisWeek = stats.value.resource_stats?.new_resources_this_week || 0;
    const newResourcesToday = stats.value.resource_stats?.new_resources_today || 0;

    // 计算y轴最大值，添加缓冲空间
    const maxValue = Math.max(total, approved, pending, newResourcesThisWeek, newResourcesToday);
    const yAxisMax = Math.max(maxValue * 1.2, maxValue + 5);

    resourceStatusChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['总资源数', '已审核通过', '待审核', '本周新增资源', '今日新增资源'],
        datasets: [{
          label: '数量',
          data: [total, approved, pending, newResourcesThisWeek, newResourcesToday],
          backgroundColor: [
            'rgba(59, 130, 246, 0.8)',   // 总资源数 - 蓝色
            'rgba(16, 185, 129, 0.8)',   // 已审核通过 - 绿色
            'rgba(251, 191, 36, 0.8)',   // 待审核 - 黄色
            'rgba(139, 92, 246, 0.8)',   // 本周新增资源 - 紫色
            'rgba(236, 72, 153, 0.8)'    // 今日新增资源 - 粉色
          ],
          borderColor: [
            'rgb(59, 130, 246)',
            'rgb(16, 185, 129)',
            'rgb(251, 191, 36)',
            'rgb(139, 92, 246)',
            'rgb(236, 72, 153)'
          ],
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return `${context.dataset.label}: ${context.parsed.y}`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            suggestedMax: yAxisMax,
            ticks: {
              stepSize: 1
            }
          }
        }
      }
    });
  }
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.admin-content {
  padding: 20px;
  margin-left: 240px;
  min-height: 100vh;
  box-sizing: border-box;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.admin-header h1 {
  margin: 0;
  color: #1e293b;
}

.refresh-btn {
  padding: 10px 20px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.refresh-btn:disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  text-align: center;
  padding: 40px 20px;
  color: #dc2626;
}

.retry-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: #dc2626;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.stats-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 24px;
  color: #1e293b;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e5e7eb;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
}

.resource-charts-container {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 20px;
  margin-top: 20px;
}

.resource-charts-container .chart-card {
  margin-top: 0;
}

.chart-title {
  font-size: 18px;
  color: #1e293b;
  margin: 0 0 20px 0;
  font-weight: 600;
}

.chart-wrapper {
  position: relative;
  height: 300px;
  width: 100%;
}

.chart-card canvas {
  max-width: 100%;
  max-height: 100%;
}

.no-data-message {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #94a3b8;
  font-size: 14px;
}

.no-data-message p {
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 36px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background-color: #f0f9ff;
}

.stat-info h3 {
  font-size: 32px;
  font-weight: bold;
  margin: 0 0 4px 0;
  color: #1e293b;
}

.stat-info p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.trends-section {
  margin-bottom: 40px;
}

.trends-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
}

.trend-chart {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.trend-chart h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #1e293b;
}

.chart-container {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 200px;
  gap: 8px;
}

.chart-bar-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.chart-bar-wrapper-dual {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.chart-bar-group {
  display: flex;
  gap: 4px;
  width: 100%;
  height: 100%;
}

.chart-bar {
  flex: 1;
  background: linear-gradient(to top, #3b82f6, #60a5fa);
  border-radius: 4px 4px 0 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  min-height: 20px;
  position: relative;
}

.chart-bar.questions {
  background: linear-gradient(to top, #3b82f6, #60a5fa);
}

.chart-bar.answers {
  background: linear-gradient(to top, #10b981, #34d399);
}

.chart-value {
  color: white;
  font-weight: bold;
  font-size: 12px;
  padding: 4px;
}

.chart-label {
  font-size: 12px;
  color: #64748b;
}

.legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #64748b;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

.legend-color.questions {
  background: linear-gradient(to top, #3b82f6, #60a5fa);
}

.legend-color.answers {
  background: linear-gradient(to top, #10b981, #34d399);
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .trends-grid {
    grid-template-columns: 1fr;
  }
  
  .resource-charts-container {
    grid-template-columns: 1fr;
  }
  
  .admin-content {
    margin-left: 0;
  }
}
</style>