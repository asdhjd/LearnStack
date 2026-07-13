<template>
  <div class="admin-dashboard">
    <AdminSidebar />
    
    <div class="admin-content">
      <header class="admin-header">
        <h1>用户管理</h1>
      </header>
      
      <main>
        <!-- 搜索 -->
        <div class="filter-section">
          <div class="search-input-group">
            <input 
              type="text" 
              class="search-input"
              placeholder="搜索用户名或邮箱..."
              v-model="searchQuery"
              @keyup.enter="handleSearch"
            />
            <button class="search-btn" @click="handleSearch">
              <i class="fas fa-search"></i> 搜索
            </button>
          </div>
          <button class="add-user-btn" @click="showAddUserDialog = true">添加用户</button>
        </div>

        <!-- 用户管理内容 -->
        <div class="user-management">
          <table class="data-table">
            <thead>
              <tr>
                <th>用户ID</th>
                <th>用户名</th>
                <th>邮箱</th>
                <th>注册时间</th>
                <th>用户类型</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <template v-if="loading">
                <tr>
                  <td colspan="6" class="empty-data">加载中...</td>
                </tr>
              </template>
              <!-- 使用分页后的数据 -->
            <template v-else-if="filteredUsers.length > 0">
                <tr v-for="user in filteredUsers" :key="user.id">
                  <td>{{ user.id }}</td>
                  <td>{{ user.username }}</td>
                  <td>{{ user.email }}</td>
                  <td>{{ formatDate(user.date_joined) }}</td>
                  <td>
                    <span :class="['user-type-badge', user.is_superuser ? 'admin' : 'normal']">
                      {{ user.is_superuser ? '管理员' : '普通用户' }}
                    </span>
                  </td>
                  <td>
                    <div class="action-buttons">
                      <button class="edit-btn" @click="editUser(user)">
                        <i class="fas fa-edit"></i> 编辑
                      </button>
                      <button class="delete-btn" @click.prevent="handleDeleteClick(user)">
                        <i class="fas fa-trash"></i> 删除
                      </button>
                    </div>
                  </td>
                </tr>
              </template>
              <template v-else>
                <tr>
                  <td colspan="6" class="empty-data">暂无符合条件的用户数据</td>
                </tr>
              </template>
            </tbody>
          </table>

          <!-- 分页 -->
          <div class="pagination" v-if="!loading && totalUsers > 0">
            <button 
              class="page-btn" 
              :disabled="currentPage === 1" 
              @click="currentPage--"
            >
              上一页
            </button>
            <span class="page-info">
              第 {{ currentPage }} 页 / 共 {{ totalPages }} 页
            </span>
            <button 
              class="page-btn" 
              :disabled="currentPage === totalPages" 
              @click="currentPage++"
            >
              下一页
            </button>
          </div>
        </div>
      </main>
    </div>

    <!-- 添加用户对话框 -->
    <div class="modal-overlay" v-if="showAddUserDialog" @click.self="closeAddUserDialog">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editingUser ? '编辑用户' : '添加用户' }}</h2>
          <button class="close-btn" @click="closeAddUserDialog">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitUserForm">
            <div class="form-group">
              <label for="username">用户名</label>
              <input 
                type="text" 
                id="username" 
                v-model="userForm.username"
                required
                placeholder="请输入用户名"
              />
            </div>
            <div class="form-group">
              <label for="email">邮箱</label>
              <input 
                type="email" 
                id="email" 
                v-model="userForm.email"
                required
                placeholder="请输入邮箱"
              />
            </div>
            <div class="form-group">
              <label for="password" v-if="!editingUser">密码</label>
              <label for="password" v-else>新密码（留空表示不修改）</label>
              <input 
                type="password" 
                id="password" 
                v-model="userForm.password"
                :required="!editingUser"
                placeholder="请输入密码"
              />
            </div>

            <div class="form-group">
              <label for="is_superuser">用户类型</label>
              <select id="is_superuser" v-model="userForm.is_superuser">
                <option value="false">普通用户</option>
                <option value="true">管理员</option>
              </select>
            </div>
            <div class="form-actions">
              <button type="button" class="cancel-btn" @click="closeAddUserDialog">取消</button>
              <button type="submit" class="submit-btn" :disabled="saving">
                {{ saving ? '保存中...' : '保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import AdminSidebar from '@/components/admin/AdminSidebar.vue';
import { adminService } from '../../services/adminService.js';
import { ElMessage, ElMessageBox } from 'element-plus';

// 状态管理
const users = ref([]);
const totalUsers = ref(0);
const loading = ref(false);
const saving = ref(false);
const showAddUserDialog = ref(false);
const editingUser = ref(null);
const searchQuery = ref(''); // 输入框绑定的变量
const searchQueryToApply = ref(''); // 实际用于搜索的变量，只有在点击搜索按钮时才更新
const currentPage = ref(1);
const pageSize = 10;

// 用户表单
const userForm = ref({
  username: '',
  email: '',
  password: '',
  is_superuser: 'false'
});

// 计算属性
const filteredUsers = computed(() => {
  let result = users.value;
  
  // 根据搜索关键词筛选
  if (searchQueryToApply.value) {
    const query = searchQueryToApply.value.toLowerCase();
    result = result.filter(user => 
      user.username.toLowerCase().includes(query) || 
      user.email.toLowerCase().includes(query)
    );
  }
  
  return result;
});

const totalPages = computed(() => {
  // 如果有后端返回的总数，使用总数计算，否则使用前端过滤后的数量
  const totalCount = totalUsers.value > 0 ? totalUsers.value : filteredUsers.value.length;
  return Math.ceil(totalCount / pageSize);
});

// 方法
const fetchUsers = async () => {
  loading.value = true;
  try {
    // 调用实际API获取用户数据
    const response = await adminService.getUsers({
      page: currentPage.value,
      page_size: pageSize
    });
    
    // 假设后端返回的数据结构是 { results: [...用户数据], count: 总数 }
    users.value = response.results || response;
    
    // 如果有总数信息，更新总页数计算
    if (response.count !== undefined) {
      totalUsers.value = response.count;
    }
    
    console.log('获取用户列表成功:', users.value);
  } catch (error) {
    console.error('获取用户列表失败:', error);
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  // 将输入框的值应用到实际搜索变量
  searchQueryToApply.value = searchQuery.value;
  currentPage.value = 1; // 搜索时重置到第一页
};



const editUser = (user) => {
  editingUser.value = user;
  userForm.value = {
    username: user.username,
    email: user.email,
    password: '',
    is_superuser: String(user.is_superuser)
  };
  showAddUserDialog.value = true;
};

const closeAddUserDialog = () => {
  showAddUserDialog.value = false;
  editingUser.value = null;
  userForm.value = {
    username: '',
    email: '',
    password: '',
    is_superuser: 'false'
  };
};

const handleDeleteClick = async (user) => {
  try {
    // 显示确认对话框
    await ElMessageBox.confirm(
      `确定要永久删除用户"${user.username}"吗？此操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
        showClose: false
      }
    );
    
    // 用户确认后执行删除
    await performDeleteUser(user.id);
  } catch (error) {
    // 用户取消操作
    if (error === 'cancel' || error.name === 'CanceledError') {
      console.log('用户取消了删除操作');
      return;
    }
    
    // 处理其他错误
    console.error('删除用户时出错:', error);
  }
};

const performDeleteUser = async (userId) => {
  try {
    await adminService.deleteUser(userId);
    // 从本地数据中移除用户
    users.value = users.value.filter(user => user.id !== userId);
    // 更新总数
    totalUsers.value--;
    
    ElMessage.success('用户删除成功');
    
    // 如果删除后当前页没有数据且不是第一页，返回上一页
    if (paginatedUsers.value.length === 0 && currentPage.value > 1) {
      currentPage.value--;
    }
  } catch (error) {
    console.error('删除用户失败:', error);
    ElMessage.error(error.message || '删除失败，请重试');
  }
};

const submitUserForm = async () => {
  saving.value = true;
  try {
    const formData = {
      ...userForm.value,
      is_superuser: userForm.value.is_superuser === 'true'
    };
    
    // 删除空密码字段（编辑时不修改密码）
    if (!formData.password) {
      delete formData.password;
    }
    
    if (editingUser.value) {
      // 编辑用户
      const updatedUser = await adminService.updateUser(editingUser.value.id, formData);
      
      // 更新本地数据
      const index = users.value.findIndex(u => u.id === editingUser.value.id);
      if (index !== -1) {
        users.value[index] = updatedUser;
      }
      
      ElMessage.success('用户信息更新成功');
    } else {
      // 添加新用户
      const newUser = await adminService.createUser(formData);
      users.value.unshift(newUser); // 添加到列表顶部
      
      // 更新总数
      totalUsers.value++;
      
      ElMessage.success('用户创建成功');
    }
    
    closeAddUserDialog();
    
    // 如果是第一页，刷新数据以确保显示最新状态
    if (currentPage.value === 1) {
      fetchUsers();
    }
  } catch (error) {
    console.error('保存用户信息失败:', error);
    ElMessage.error(error.message || '保存失败，请重试');
  } finally {
    saving.value = false;
  }
};



const formatDate = (dateString) => {
  // 检查日期字符串是否存在且有效
  if (!dateString) {
    return '暂无注册时间';
  }
  
  const date = new Date(dateString);
  
  // 检查是否是有效的日期
  if (isNaN(date.getTime())) {
    // 尝试处理Django默认的日期格式（ISO格式）
    try {
      // 处理可能的格式差异，如将'YYYY-MM-DD HH:MM:SS'转换为ISO格式
      if (typeof dateString === 'string' && /\d{4}-\d{2}-\d{2}/.test(dateString)) {
        const isoDate = dateString.replace(/(\d{4}-\d{2}-\d{2})\s*(\d{2}:\d{2}:\d{2})?/, '$1T$2Z');
        return new Date(isoDate).toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        });
      }
      return '日期格式无效';
    } catch {
      return '日期格式无效';
    }
  }
  
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 生命周期
  onMounted(() => {
    fetchUsers();
  });

  // 监听页码变化
  watch(() => currentPage.value, () => {
    fetchUsers();
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

.add-user-btn {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background-color 0.2s;
  height: 40px;
}

.add-user-btn:hover {
  background-color: #2563eb;
}

.filter-section {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}

/* 统一的搜索容器样式 */
.search-input-group,
.search-container {
  display: flex;
  align-items: center;
  gap: 0;
}

/* 统一的搜索输入框样式 */
.search-input {
  padding: 11px 16px;
  border: 1px solid #d1d5db;
  border-radius: 4px 0 0 4px;
  width: 300px;
  font-size: 14px;
  border-right: none;
  box-sizing: border-box;
  height: 40px;
}

/* 统一的搜索按钮样式 */
.search-btn {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background-color 0.2s;
  height: 40px;
}

.search-btn:hover {
  background-color: #2563eb;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background-color: white;
  font-size: 14px;
}

.filter-btn {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.3s;
}

.filter-btn:hover {
  background-color: #2563eb;
}

.data-table {
  width: 100%;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border-collapse: collapse;
  margin-bottom: 20px;
}

.data-table th,
.data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
}

.data-table tbody tr:hover {
  background-color: #f9fafb;
}

.empty-data {
  text-align: center;
  color: #6b7280;
  padding: 40px 0;
}

/* 用户类型标签 */
.user-type-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.user-type-badge.normal {
  background-color: #dbeafe;
  color: #1d4ed8;
}

.user-type-badge.admin {
  background-color: #fef3c7;
  color: #92400e;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 8px;
}

.edit-btn, .delete-btn {
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    transition: background-color 0.3s;
  }

  .edit-btn {
    background-color: #3b82f6;
    color: white;
  }

  .edit-btn:hover {
    background-color: #2563eb;
  }

.delete-btn {
  background-color: #ef4444;
  color: white;
}

.delete-btn:hover {
  background-color: #dc2626;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #e5e7eb;
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #6b7280;
  font-size: 14px;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.close-btn:hover {
  background-color: #f3f4f6;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group select {
  width: 95%;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

.cancel-btn,
.submit-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.3s;
}

.cancel-btn {
  background-color: #f3f4f6;
  color: #374151;
}

.cancel-btn:hover {
  background-color: #e5e7eb;
}

.submit-btn {
  background-color: #3b82f6;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>