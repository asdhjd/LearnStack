import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import '@fortawesome/fontawesome-free/css/all.css'; // 图标库
import axios from 'axios';
import { createPinia } from 'pinia';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';

axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || '/api';

const app = createApp(App);
app.config.globalProperties.mediaUrl = (import.meta.env.VITE_API_BASE_URL || '/api').replace('/api', '') + '/media/';

const pinia = createPinia(); // 新增：创建 Pinia 实例
app.use(pinia);
app.use(ElementPlus); // 安装 Element Plus 组件库

app.use(router).mount('#app');
