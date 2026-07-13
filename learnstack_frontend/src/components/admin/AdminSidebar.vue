<template>
  <div class="admin-sidebar">
    <h2>后台管理</h2>
    <nav>
      <ul>
        <li><router-link to="/admin/dashboard">数据统计仪表盘</router-link></li>
        <li><router-link to="/admin/users">用户管理</router-link></li>
        <li><router-link to="/admin/categories">分类管理</router-link></li>
        <li><router-link to="/admin/resources">资源管理</router-link></li>
        <li><router-link to="/admin/forum">论坛管理</router-link></li>
        <li><router-link to="/admin/resourcesmoderate">资源审核</router-link></li>
        <li><router-link to="/admin/resourcerequests">处理资源申请</router-link></li>
        <li class="logout-item"><a @click="handleLogout" class="logout-link">退出登录</a></li>
      </ul>
    </nav>
  </div>
</template>

<script>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'AdminSidebar',
  setup() {
    const router = useRouter();
    
    // 检查用户是否为管理员
    const isAdmin = () => {
      const userInfo = localStorage.getItem('user_info');
      if (userInfo) {
        try {
          const user = JSON.parse(userInfo);
          return user && user.is_superuser === true;
        } catch (error) {
          console.error('解析用户信息失败:', error);
          return false;
        }
      }
      return false;
    };
    
    // 退出登录函数
    const handleLogout = () => {
      // 清除本地存储中的登录信息
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      // 跳转到登录页面
      router.push('/login');
    };
    
    // 组件挂载时检查管理员权限
    onMounted(() => {
      // 检查当前用户是否为管理员
      if (!isAdmin()) {
        // 如果不是管理员，重定向到登录页面
        router.push('/login');
      }
    });
    
    return {
      handleLogout
    };
  }
};
</script>

<style scoped>
.admin-sidebar {
  width: 240px;
  background-color: #1e293b;
  color: white;
  padding: 20px;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  overflow-y: auto;
  z-index: 100;
  box-sizing: border-box;
}

.admin-sidebar h2 {
  margin-bottom: 30px;
  color: white;
}

.admin-sidebar ul {
  list-style: none;
  padding: 0;
}

.admin-sidebar li {
  margin-bottom: 10px;
}

.admin-sidebar a {
  color: #e2e8f0;
  text-decoration: none;
  display: block;
  padding: 12px 16px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.admin-sidebar a:hover,
.admin-sidebar a.router-link-active {
  background-color: #3b82f6;
  color: white;
}

/* 退出登录按钮特殊样式 */
.logout-item {
  margin-top: 20px;
  border-top: 1px solid #e0e0e0;
  padding-top: 15px; /* 添加与上边线的边距 */
}

.logout-link {
  color: #dc3545 !important;
  cursor: pointer; /* 鼠标指针样式 */
}

.logout-link:hover {
  background-color: #ffe5e7 !important;
  color: #c82333 !important;
  border-left-color: #dc3545 !important;
}

/* 为所有a标签设置指针样式 */
.admin-sidebar a {
  cursor: pointer;
}
</style>