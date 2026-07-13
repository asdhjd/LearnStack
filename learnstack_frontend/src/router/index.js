import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';// 首页
import AllCategoriesView from '../views/AllCategories.vue';// 所有技术分类
import AllTechnologiesView from '../views/AllTechnologies.vue';// 所有技术
import CategoryDetail from '../views/CategoryDetail.vue';// 分类详情
import ResourceList from '../views/ResourceList.vue';// 学习资源库
import Login from '../views/Login.vue';// 登录页
import Register from '../views/Register.vue';// 注册页
import PersonalInfo from '../views/PersonalInfo.vue';// 个人信息
import SearchResults from '../views/SearchResults.vue';
import CommunityForum from '../views/CommunityForum.vue';
import QuestionDetail from '../views/QuestionDetail.vue';
import AIAssistant from '../views/AIAssistant.vue';



// 检查用户是否已登录
const isAuthenticated = () => {
  return !!localStorage.getItem('access_token');
};

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior() {
    // 始终滚动到顶部
    return { top: 0 }
  },
  routes: [
    { path: '/', name: 'Home', component: Home },
    { path: '/search', name: 'SearchResults', component: SearchResults, meta: { title: '搜索结果' } }, // 新增
    {
    path: '/allCategories',
    name: 'AllCategories',
    component: AllCategoriesView,
    meta: {title: '所有技术分类'},
    },
    {
    path: '/learningpath/:categoryId',
    name: 'LearningPathDetail',
    component: () => import('../views/LearningPathDetail.vue'),
    meta: {title: '学习路径详情'}
    },
    {
    path: '/allTechnologies',
    name: 'AllTechnologies',
    component: AllTechnologiesView,
    meta: {title: '所有技术'},
    },
    {
    path: '/categories/:id',
    name: 'CategoryDetail',
    component: CategoryDetail,
    meta: {title: '分类详情'}
    },
    {
    path: '/resources',
    name: 'ResourceList',
    component: ResourceList,
    meta: {title: '学习资源库'}
    },
    {
    path: '/resources/:id',
    name: 'ResourceDetail',
    component: () => import('../views/ResourceDetail.vue'),
    meta: {title: '资源详情'}
    },
    {
    path: '/resources/submit',
    name: 'SubmitResource',
    component: () => import('../views/SubmitResource.vue'),
    meta: {title: '投稿资源', requiresAuth: true}
    },
    {
      path: '/login',
      name: 'Login',
      component: Login,
      meta: {title: '登录'}
    },
    {
      path: '/register',
      name: 'Register',
      component: Register,
      meta: {title: '注册'}
    },
    {
      path: '/personalinfo',
      name: 'PersonalInfo',
      component: PersonalInfo,
      meta: {title: '个人中心'}
    },
    {
      path: '/community',
      name: 'CommunityForum',
      component: CommunityForum,
      meta: {title: '社区问答'}
    },
    {
      path: '/community/:id',
      name: 'QuestionDetail',
      component: QuestionDetail,
      meta: {title: '问题详情'}
    },
    { path: '/community/ask', name: 'AskQuestion', component: () => import('../views/AskQuestion.vue'), meta: {title: '发布问题', requiresAuth: true} },
    { path: '/aiassistant', name: 'AIAssistant', component: AIAssistant, meta: {title: 'AI学习助手', requiresAuth: true} },
    // 管理员页面路由
    { path: '/admin/dashboard', name: 'AdminDashboard', component: () => import('../views/admin/AdminDashboard.vue'), meta: {title: '数据统计仪表盘', requiresAuth: true, requiresAdmin: true} },
    { path: '/admin/users', name: 'UserManagement', component: () => import('../views/admin/UserManagement.vue'), meta: {title: '用户管理', requiresAuth: true, requiresAdmin: true} },
      { path: '/admin/resources', name: 'ResourceManagement', component: () => import('../views/admin/ResourceManagement.vue'), meta: {title: '资源管理', requiresAuth: true, requiresAdmin: true} },
      { path: '/admin/resourcesmoderate', name: 'ResourceModeration', component: () => import('../views/admin/ResourceModeration.vue'), meta: {title: '资源审核', requiresAuth: true, requiresAdmin: true} },
      { path: '/admin/resourcerequests', name: 'ResourceRequestManagement', component: () => import('../views/admin/ResourceRequestManagement.vue'), meta: {title: '资源添加申请', requiresAuth: true, requiresAdmin: true} },
      { path: '/admin/categories', name: 'CategoryManagement', component: () => import('../views/admin/CategoryManagement.vue'), meta: {title: '分类管理', requiresAuth: true, requiresAdmin: true} },
      { path: '/admin/forum', name: 'ForumManagement', component: () => import('../views/admin/ForumManagement.vue'), meta: {title: '论坛管理', requiresAuth: true, requiresAdmin: true} },
]
});

// 检查用户是否为管理员
const isAdmin = () => {
  try {
    const userInfo = localStorage.getItem('user_info');
    if (userInfo) {
      const user = JSON.parse(userInfo);
      return user.is_superuser || false;
    }
    return false;
  } catch (error) {
    console.error('检查管理员权限时出错:', error);
    return false;
  }
};

// 导航守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - LearnStack` : 'LearnStack';
  
  // 检查路由是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 此路由需要认证，检查是否已登录
    if (!isAuthenticated()) {
      // 未登录，先显示确认对话框
      if (confirm('请先登录以继续操作')) {
        // 用户点击确认，重定向到登录页面，并带上重定向参数
        next({
          path: '/login',
          query: { redirect: to.fullPath }
        });
      } else {
        // 用户点击取消，阻止导航
        next(false);
      }
    } else {
      // 已登录，检查是否需要管理员权限
      if (to.matched.some(record => record.meta.requiresAdmin)) {
        // 需要管理员权限，检查是否为管理员
        if (!isAdmin()) {
          alert('您没有管理员权限，无法访问此页面');
          next(false);
        } else {
          // 是管理员，继续访问
          next();
        }
      } else {
        // 不需要管理员权限，直接访问
        next();
      }
    }
  } else {
    // 不需要认证的路由，直接访问
    next();
  }
});

export default router;