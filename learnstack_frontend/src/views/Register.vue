<template>
  <div class="register-page">
    <h1>注册</h1>
    <form @submit.prevent="handleRegister">
      <input v-model="username" type="text" placeholder="用户名（必填）" required>
      <input v-model="email" type="email" placeholder="邮箱（可选）">  <!-- 新增邮箱输入 -->
      <input v-model="password" type="password" placeholder="密码" required>
      <input v-model="confirmPassword" type="password" placeholder="确认密码" required>
      <button type="submit">注册</button>
    </form>
    <p v-if="error">{{ error }}</p>
    <router-link to="/login">已有账号？登录</router-link>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { register } from '@/services/userService';

defineOptions({
  name: 'RegisterPage'
});

const router = useRouter();
const username = ref('');  // 用户名（必填）
const email = ref('');      // 邮箱（可选）
const password = ref('');
const confirmPassword = ref('');
const error = ref('');
const emailReg = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;  // 邮箱正则

const handleRegister = async () => {
  if (email.value && !emailReg.test(email.value)) {  // 邮箱非空时校验格式
    error.value = '邮箱格式不正确';
    return;
  }
  if (!username.value.trim()) {
    error.value = '用户名不能为空';
    return;
  }
  if (password.value.length < 6) {  // 新增密码长度校验
    error.value = '密码至少需要6位';
    return;
  }
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致';
    return;
  }
  try {
    // 传递用户名、邮箱（可选）、密码
    await register({ username: username.value, email: email.value, password: password.value });
    router.push('/login');
  } catch (errorMessage) {
    error.value = errorMessage;
  }
};
</script>

<style scoped>
.register-page {
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