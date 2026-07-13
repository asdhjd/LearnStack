<template>
  <div class="login-page">
    <h1>登录</h1>
    <form @submit.prevent="handleLogin">
      <input v-model="username" type="text" placeholder="账号" required>  <!-- 修改：用户名→账号 -->
      <input v-model="password" type="password" placeholder="密码" required>
      <button type="submit">登录</button>
    </form>
    <p v-if="error">{{ error }}</p>
    <router-link to="/register">没有账号？注册</router-link>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { login } from '@/services/userService';

defineOptions({
  name: 'LoginPage'
});

const router = useRouter();
const username = ref('');  // 用户名（必填）
const password = ref('');
const error = ref('');

const handleLogin = async () => {
  if (!username.value.trim()) {
    error.value = '用户名不能为空';
    return;
  }
  try {
    const response = await login({ username: username.value, password: password.value });
    // 修复：后端返回的令牌字段是 response.access（来自 userService 的 login 函数返回 response.data）
    localStorage.setItem('access_token', response.access);  // 原错误：response.access_token
    
    // 检查是否有用户信息，如果有检查是否为管理员
    if (response.user) {
      localStorage.setItem('user_info', JSON.stringify(response.user));
      // 如果是管理员，直接跳转到管理员后台
      if (response.user.is_superuser) {
        router.push('/admin/dashboard');
        return;
      }
    }
    
    // 普通用户或没有用户信息时，跳转到首页
    router.push('/');
  } catch (errorMessage) {
    error.value = errorMessage;
  }
};
</script>

<style scoped>
.login-page {
  padding: 40px 8%;
  max-width: 400px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 20px;
}

input {
  width: 100%;
  padding: 10px;
  margin-bottom: 15px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #2563eb;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #1d4ed8;
}

p {
  color: red;
  margin-top: 10px;
}

router-link {
  display: block;
  margin-top: 15px;
  color: #2563eb;
  text-decoration: none;
}

router-link:hover {
  text-decoration: underline;
}
</style>