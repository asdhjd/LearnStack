<template>
  <div id="app">
    <nav v-if="!isAdminRoute" class="navbar">
      <div class="nav-left">
        <div class="logo" @click="$router.push('/')">LearnStack</div>
        <div class="nav-menu">
          <a class="nav-link" @click="$router.push('/resources')">资源库</a>
          <a class="nav-link" @click="$router.push('/aiassistant')">AI助手</a>
          <a class="nav-link" @click="$router.push('/community')">社区</a>
        </div>
      </div>
      
      <div class="search-container">
        <input type="text" class="nav-search" placeholder="搜索资源...">
        <button class="search-btn" @click="handleSearch">
          <i class="fas fa-search"></i>
        </button>
      </div>
      
      <!-- 登录状态判断 -->
      <div v-if="currentUser" class="user-container">
        <div class="username" @mouseenter="showDropdown = true" @mouseleave="showDropdown = false">
          <img 
            :src="currentUser.avatar || '/default-avatar.png'" 
            class="user-avatar" 
            alt="用户头像"
          />
          {{ currentUser.nickname || currentUser.username }} ▼  <!-- 修改：显示昵称，无则显示用户名 -->
        </div>
        <!-- 下拉菜单 -->
        <div 
          v-show="showDropdown" 
          class="dropdown-menu"
          @mouseenter="showDropdown = true"
          @mouseleave="showDropdown = false"
        >
          <a @click="$router.push('/personalinfo')">个人中心</a>
          <a @click="handleLogout">退出登录</a>
        </div>
      </div>
      <button v-else class="nav-btn" @click="$router.push('/login')">登录/注册</button>
    </nav>

    <router-view />

    <footer class="footer">
      LearnStack | 技术学习平台
    </footer>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';  // 新增：引入 useRouter
import { getUserInfo } from '@/services/userService';
import { useUserStore } from '@/stores/user';  // 新增：引入用户存储

export default {
  name: 'App',
  setup() {
    const currentUser = ref(null);
    const showDropdown = ref(false);
    const route = useRoute();
    const router = useRouter();  // 新增：初始化路由实例
    const store = useUserStore();  // 新增：初始化存储实例
    
    // 计算属性：判断当前路由是否为管理员路由
    const isAdminRoute = computed(() => {
      return route.path.startsWith('/admin/');
    });

    // 初始化获取用户信息
    onMounted(async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          currentUser.value = await getUserInfo();
          store.setCurrentUser(currentUser.value);  // 同步到存储
          localStorage.setItem('user_info', JSON.stringify(currentUser.value));  // 存储到localStorage
        } catch (error) {
          console.error('获取用户信息失败:', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('user_info');  // 清除用户信息
          router.push('/login');  // 使用正确的 router 实例
        }
      }
    });

    // 监听路由变化，重新加载用户信息
    watch(route, async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          currentUser.value = await getUserInfo();
          store.setCurrentUser(currentUser.value);  // 同步到存储
          localStorage.setItem('user_info', JSON.stringify(currentUser.value));  // 存储到localStorage
        } catch (error) {
          console.error('路由变化后获取用户信息失败:', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('user_info');  // 清除用户信息
          router.push('/login');  // 使用正确的 router 实例
        }
      } else {
        currentUser.value = null;
        store.setCurrentUser(null);  // 清除存储状态
        localStorage.removeItem('user_info');  // 清除用户信息
      }
    });

    // 退出登录
    const handleLogout = () => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');  // 清除用户信息
      currentUser.value = null;
      showDropdown.value = false;
      router.push('/login');
    };

    return { currentUser, showDropdown, handleLogout, isAdminRoute };
  },
  methods: {
    handleSearch() {
      const searchInput = document.querySelector('.nav-search');
      const searchValue = searchInput.value.trim();
      if (searchValue) {
        this.$router.push({ name: 'SearchResults', query: { q: searchValue } });
        // 清空搜索框内容
        searchInput.value = '';
      }
    }
  }
}
</script>

<style scoped>
/* 新增用户容器样式 */
.user-container {
  position: relative;
  margin-left: 20px;
}

.username {
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.username:hover {
  background-color: #f0f2f5;
}

/* 下拉菜单样式 */
.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-radius: 4px;
  min-width: 120px;
  padding: 8px 0;
  z-index: 1000;
  cursor: pointer;
}

.dropdown-menu a {
  display: block;
  padding: 8px 16px;
  color: #333;
  text-decoration: none;
  transition: background-color 0.2s;
}

.dropdown-menu a:hover {
  background-color: #f0f2f5;
}
</style>

<style scoped>
/* 全局导航栏样式 */
.navbar {
  height: 80px;
  padding: 0 8%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  background: white;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 40px;
}

.logo {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2563eb;
  cursor: pointer;
}

.nav-menu {
  display: flex;
  gap: 30px;
}

.nav-link {
  color: #111827;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  transition: color 0.3s;
  cursor: pointer;
}

.nav-link:hover {
  color: #2563eb;
  text-decoration: underline;
}

/* 搜索框容器样式 */
.search-container {
  position: relative;
  display: flex;
  align-items: center;
}

.nav-search {
  width: 300px;
  height: 48px;
  border: 2px solid #e5e7eb;
  border-radius: 24px;
  padding: 0 50px 0 20px; /* 右侧留出按钮空间 */
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s;
}

.nav-search:focus {
  border-color: #2563eb;
}

/* 搜索按钮样式 */
.search-btn {
  position: absolute;
  right: 8px;
  width: 32px;
  height: 32px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.3s;
}

.search-btn:hover {
  background: #2625ebff;
}

.nav-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  background: #000;
  color: white;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.3s;
}

.nav-btn:hover {
  background: #222;
}

/* 全局页脚样式 */
.footer {
  padding: 20px 8%;
  text-align: center;
  color: #6b7280;
  font-size: 0.9rem;
  border-top: 1px solid #e5e7eb;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }
  
  .search-container {
    flex: 1;
    margin: 0 16px;
  }
  
  .nav-search {
    width: 100%;
  }
}
</style>

<style scoped>
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 8px;
  vertical-align: middle;
}
</style>