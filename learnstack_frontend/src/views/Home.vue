<template>
  <div class="home-page">
    <section class="hero-section">
      <div class="hero-text">
        <p class="hero-eyebrow">AI 驱动 · 学习路径 · 社区互助</p>
        <h1>开启你的下一段技术成长旅程</h1>
        <p class="hero-subtitle">
          聚合精选学习资源、学习路径与实时 AI 助手，让你在最短时间构建系统化的技术能力。
        </p>
        <div class="hero-actions">
          <button class="primary-btn" @click="goToRoute('AIAssistant')">
            <i class="fas fa-robot"></i> 立即向 AI 提问
          </button>
          <button class="secondary-btn" @click="goToRoute('CommunityForum')">
            <i class="fas fa-users"></i> 加入社区讨论
          </button>
        </div>
        <div class="hero-meta">
          <span><strong>{{ statsCards[1].value }}</strong> 学习路径</span>
          <span><strong>{{ statsCards[0].value }}</strong> 精选课程</span>
          <span><strong>{{ statsCards[2].value }}</strong> 社区讨论</span>
        </div>
      </div>
      <div class="hero-panel">
        <div class="hero-panel-header">
          <span>今日推荐</span>
          <button class="link-btn" @click="goToRoute('AllCategories')">查看全部</button>
        </div>
        <ul class="hero-panel-list" v-if="highlightCategories.length">
          <li
            v-for="category in highlightCategories"
            :key="category.id"
            @click="goToCategory(category.id)"
          >
            <div class="panel-title">{{ category.name }}</div>
            <p class="panel-desc">
              {{ category.description || '涵盖零基础到实战的完整路线' }}
            </p>
            <span class="panel-link">开始学习 <i class="fas fa-arrow-right"></i></span>
          </li>
        </ul>
        <div v-else class="hero-panel-empty">分类数据加载中...</div>
      </div>
    </section>

    <section class="stats-grid">
      <div class="stat-card" v-for="stat in statsCards" :key="stat.label">
        <span class="stat-label">{{ stat.label }}</span>
        <p class="stat-value">{{ stat.value }}</p>
        <span class="stat-desc">{{ stat.desc }}</span>
      </div>
    </section>

    <section class="content-grid">
      <div class="panel-card">
        <div class="panel-header">
          <div>
            <h2>技术分类</h2>
          </div>
          <button class="link-btn" @click="goToRoute('AllCategories')">全部分类</button>
        </div>
        <CategoryList
          :categories="parentCategories"
          :showTitle="false"
          @categoryClick="goToCategory"
        />
      </div>

      <div class="panel-card">
        <div class="panel-header">
          <div>
            <h2>高频学习主题</h2>
          </div>
          <button class="link-btn" @click="goToRoute('AllTechnologies')">全部技术</button>
        </div>
        <HotSubcategoryList @subcategoryClick="goToSubcategory" />
      </div>
    </section>

    <section class="cta-grid">
      <div class="cta-card" v-for="action in actionCards" :key="action.title">
        <div class="cta-icon" :class="action.iconClass">
          <i :class="action.icon"></i>
        </div>
        <div class="cta-content">
          <h3>{{ action.title }}</h3>
          <p>{{ action.desc }}</p>
          <button class="link-btn" @click="goToRoute(action.route)">
            {{ action.cta }} <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getParentCategories, getAllTechnologies } from '@/services/category';
import communityService from '@/services/communityService';
import { resourceService } from '@/services/resource';
import CategoryList from '@/components/categories/CategoryList.vue';
import HotSubcategoryList from '@/components/categories/HotSubcategoryList.vue';

defineOptions({
  name: 'HomePage'
});

const router = useRouter();
const parentCategories = ref([]);
const stats = ref({
  resources: '--',
  learningPaths: '--',
  communityPosts: '--'
});

const formatNumber = (value) => {
  if (typeof value !== 'number') return value || '--';
  return value.toLocaleString();
};

const statsCards = computed(() => [
  {
    label: '精选课程',
    value: formatNumber(stats.value.resources),
    desc: '平台已收录的站内资源'
  },
  {
    label: '学习路径',
    value: formatNumber(stats.value.learningPaths),
    desc: '适配不同阶段的成长路线'
  },
  {
    label: '社区讨论',
    value: formatNumber(stats.value.communityPosts),
    desc: '活跃话题与问答总量'
  }
]);

const actionCards = [
  {
    title: 'AI 学习助手',
    desc: '结合站内资源，实时回答学习疑问，并指向对应的学习路径。',
    route: 'AIAssistant',
    cta: '立即提问',
    icon: 'fas fa-robot',
    iconClass: 'accent-blue'
  },
  {
    title: '投稿学习资源',
    desc: '分享你的优质内容，或申请管理员协助，丰富学习生态。',
    route: 'SubmitResource',
    cta: '我要投稿',
    icon: 'fas fa-upload',
    iconClass: 'accent-pink'
  }
];

const goToRoute = (name) => {
  if (!name) return;
  if (name === 'ResourceList') {
    router.push('/allCategories');
    return;
  }
  router.push({ name });
};

const goToCategory = (categoryId) => {
  router.push({ name: 'CategoryDetail', params: { id: categoryId } });
};

const goToSubcategory = (subcategoryId) => {
  router.push({ name: 'SubcategoryDetail', params: { id: subcategoryId } });
};

const highlightCategories = computed(() =>
  pickRandom(parentCategories.value, 3)
);

const pickRandom = (list, count) => {
  if (!Array.isArray(list) || list.length === 0) return [];
  const copy = [...list];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy.slice(0, count);
};

const loadStats = async () => {
  try {
    const [resourceData, communityData, technologiesData] = await Promise.all([
      resourceService.getAllResources(),
      communityService.getQuestions({ page_size: 1 }),
      getAllTechnologies()
    ]);

    const resolveCount = (data) => {
      if (!data) return 0;
      if (typeof data.count === 'number') return data.count;
      if (Array.isArray(data.results)) return data.results.length;
      if (Array.isArray(data)) return data.length;
      return 0;
    };

    // 学习路径数量 = 所有技术分类的数量（每个技术对应一个学习路径）
    const learningPathsCount = Array.isArray(technologiesData) 
      ? technologiesData.length 
      : resolveCount(technologiesData);

    stats.value = {
      resources: resolveCount(resourceData),
      learningPaths: learningPathsCount,
      communityPosts: resolveCount(communityData)
    };
  } catch (error) {
    console.error('加载主页统计数据失败:', error);
  }
};

onMounted(async () => {
  const catRes = await getParentCategories();
  parentCategories.value = catRes.data || [];
  await loadStats();
});
</script>

<style scoped>
.home-page {
  padding: 1.5rem 0 3rem;
  min-height: calc(100vh - 140px);
  background: linear-gradient(180deg, #f6f8fc 0%, #ffffff 45%, #f8fafc 100%);
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.hero-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  align-items: stretch;
  padding: 2rem;
  border-radius: 24px;
  background: linear-gradient(135deg, #1d4ed8, #3b82f6, #60a5fa);
  color: #fff;
  box-shadow: 0 30px 60px rgba(23, 37, 84, 0.25);
}

.hero-text h1 {
  font-size: 2.4rem;
  margin: 0.5rem 0 0.75rem;
  line-height: 1.2;
}

.hero-subtitle {
  margin: 0;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
}

.hero-eyebrow {
  font-size: 0.9rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.hero-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin: 1.5rem 0 0.5rem;
}

.primary-btn,
.secondary-btn {
  border: none;
  border-radius: 999px;
  padding: 0.85rem 1.6rem;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.primary-btn {
  background: #0f172a;
  color: #fff;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.35);
}

.primary-btn:hover {
  transform: translateY(-1px);
}

.secondary-btn {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.hero-meta {
  display: flex;
  gap: 1.5rem;
  margin-top: 1.25rem;
  flex-wrap: wrap;
  font-size: 0.95rem;
}

.hero-meta strong {
  font-size: 1.2rem;
}

.hero-panel {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(6px);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.15);
}

.hero-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  margin-bottom: 1rem;
}

.hero-panel-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.hero-panel-list li {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 14px;
  padding: 0.9rem 1rem;
  cursor: pointer;
  transition: transform 0.2s, background 0.2s;
}

.hero-panel-list li:hover {
  transform: translateX(4px);
  background: rgba(255, 255, 255, 0.25);
}

.panel-title {
  font-weight: 600;
  color: #fff;
}

.panel-desc {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.85);
  margin: 0.2rem 0 0.3rem;
}

.panel-link {
  font-size: 0.85rem;
  color: #e0edff;
}

.hero-panel-empty {
  text-align: center;
  color: rgba(255, 255, 255, 0.75);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: #fff;
  border-radius: 16px;
  padding: 1.2rem 1.4rem;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.07);
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.stat-label {
  font-size: 0.85rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.stat-value {
  font-size: 1.8rem;
  margin: 0.25rem 0;
  color: #0f172a;
}

.stat-desc {
  font-size: 0.9rem;
  color: #475569;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
}

.panel-card {
  background: #fff;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 16px 32px rgba(15, 23, 42, 0.08);
  border: 1px solid rgba(226, 232, 240, 0.9);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.25rem;
}


.panel-header h2 {
  margin: 0.25rem 0 0;
  font-size: 1.4rem;
  color: #0f172a;
}

.link-btn {
  border: none;
  background: none;
  color: #2563eb;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0;
}

.cta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.25rem;
}

.cta-card {
  background: #0f172a;
  color: #fff;
  border-radius: 18px;
  padding: 1.25rem;
  display: flex;
  gap: 1rem;
  align-items: center;
  box-shadow: 0 20px 35px rgba(15, 23, 42, 0.4);
}

.cta-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.12);
  font-size: 1.2rem;
}

.cta-icon.accent-blue {
  background: rgba(96, 165, 250, 0.25);
  color: #bfdbfe;
}

.cta-icon.accent-pink {
  background: rgba(244, 114, 182, 0.25);
  color: #fbcfe8;
}

.cta-content h3 {
  margin: 0 0 0.3rem;
  font-size: 1.15rem;
}

.cta-content p {
  margin: 0 0 0.6rem;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.85);
}

@media (max-width: 768px) {
  .hero-section {
    padding: 1.5rem;
  }

  .hero-text h1 {
    font-size: 2rem;
  }

  .hero-meta {
    flex-direction: column;
    gap: 0.5rem;
  }

  .primary-btn,
  .secondary-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
