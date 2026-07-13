<template>
  <div class="admin-dashboard">
    <AdminSidebar />
    
    <div class="admin-content">
      <header class="admin-header">
        <h1>分类管理</h1>
      </header>

      <!-- 搜索和筛选 -->
      <div class="filter-section" style="display: flex; align-items: center; gap: 10px;">
        <div class="search-input-group">
          <div class="search-container">
            <input 
              v-model="searchQuery" 
              type="text" 
              class="search-input"
              placeholder="搜索分类名称..."
              @keyup.enter="handleSearch"
            />
            <button class="search-btn" @click="handleSearch">
              <i class="fas fa-search"></i> 搜索
            </button>
          </div>
        </div>
        <button class="add-btn" @click="showAddDialog = true">
          添加分类
        </button>
      </div>

      <!-- 分类列表 -->
      <div class="category-list">
        <div class="accordion">
          <!-- 一级分类折叠面板 -->
          <div 
            v-for="parentCategory in parentCategoriesList" 
            :key="parentCategory.id"
            class="accordion-item"
          >
            <div 
              class="accordion-header" 
              @click="toggleAccordion(parentCategory.id)"
            >
              <i :class="['fas', 'fa-chevron-down', { 'rotate-180': expandedCategories.includes(parentCategory.id) }]"></i>
              <div class="category-info">
                <div class="category-title">
                  <img 
                    v-if="parentCategory.icon_image_url"
                    :src="parentCategory.icon_image_url" 
                    :alt="parentCategory.name"
                    class="category-icon-img"
                  />
                  <div v-else class="category-icon-placeholder">{{ parentCategory.name.charAt(0) }}</div>
                  <span>{{ parentCategory.name }}</span>
                  <span class="category-badge primary">一级分类</span>
                </div>
                <div class="category-meta">
                  <span class="hot-status">{{ parentCategory.is_hot ? '热门' : '非热门' }}</span>
                  <span class="description">{{ parentCategory.description || '无描述' }}</span>
                </div>
              </div>
              <div class="category-actions">
                <label class="switch">
                  <input 
                    type="checkbox" 
                    :checked="parentCategory.is_hot"
                    @change.stop="toggleHotStatus(parentCategory.id, !parentCategory.is_hot)"
                  />
                  <span class="slider round"></span>
                </label>
                <button class="edit-btn" @click.stop="editCategory(parentCategory)">
                  <i class="fas fa-edit"></i> 编辑
                </button>
                <button class="delete-btn" @click.stop="deleteCategory(parentCategory.id)">
                  <i class="fas fa-trash"></i> 删除
                </button>
              </div>
            </div>
            
            <!-- 二级分类内容 -->
            <div 
              v-show="expandedCategories.includes(parentCategory.id)" 
              class="accordion-content"
            >
              <div class="subcategories-container">
                <div 
                  v-for="subcategory in getSubcategories(parentCategory.id)" 
                  :key="subcategory.id"
                  class="subcategory-item"
                >
                  <div class="category-info">
                    <div class="category-title">
                      <img 
                        v-if="subcategory.icon_image_url"
                        :src="subcategory.icon_image_url" 
                        :alt="subcategory.name"
                        class="category-icon-img"
                      />
                      <div v-else class="category-icon-placeholder">{{ subcategory.name.charAt(0) }}</div>
                      <span>{{ subcategory.name }}</span>
                      <span class="category-badge secondary">二级分类</span>
                    </div>
                    <div class="category-meta">
                      <span class="hot-status">{{ subcategory.is_hot ? '热门' : '非热门' }}</span>
                      <span class="description">{{ subcategory.description || '无描述' }}</span>
                    </div>
                  </div>
                  <div class="category-actions">
                    <label class="switch">
                      <input 
                        type="checkbox" 
                        :checked="subcategory.is_hot"
                        @change.stop="toggleHotStatus(subcategory.id, !subcategory.is_hot)"
                      />
                      <span class="slider round"></span>
                    </label>
                    <button class="edit-btn" @click.stop="editCategory(subcategory)">
                      <i class="fas fa-edit"></i> 编辑
                    </button>
                    <button class="delete-btn" @click.stop="deleteCategory(subcategory.id)">
                      <i class="fas fa-trash"></i> 删除
                    </button>
                  </div>
                </div>
                
                <!-- 无二级分类时的提示 -->
                <div v-if="getSubcategories(parentCategory.id).length === 0" class="no-subcategories">
                  <p>暂无二级分类</p>
                </div>
                
                <!-- 添加二级分类按钮 -->
                <div class="add-subcategory-section">
                  <button class="add-subcategory-btn" @click="addSubcategory(parentCategory.id)">
                    添加二级分类
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 没有一级分类时的提示 -->
          <div v-if="parentCategoriesList.length === 0" class="no-categories">
            <p>暂无分类数据</p>
          </div>
        </div>
      </div>

      <!-- 添加/编辑分类对话框 -->
      <div class="modal" v-if="showDialog">
        <div class="modal-content">
          <div class="modal-header">
            <h2>{{ editingCategory ? '编辑分类' : '添加分类' }}</h2>
            <button class="close-btn" @click="closeDialog">&times;</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveCategory">
              <div class="form-group">
                <label for="categoryName">分类名称 *</label>
                <input 
                  type="text" 
                  id="categoryName" 
                  v-model="formData.name"
                  required
                  placeholder="请输入分类名称"
                />
              </div>
              <div class="form-group">
                <label for="categoryDescription">描述</label>
                <textarea 
                  id="categoryDescription" 
                  v-model="formData.description"
                  rows="3"
                  placeholder="请输入分类描述"
                ></textarea>
              </div>
              <div class="form-group">
                <label for="categoryIcon">分类图标图片</label>
                <input 
                  type="file" 
                  id="categoryIcon" 
                  accept="image/*"
                  @change="handleIconUpload"
                />
                <div v-if="formData.icon_image_url" class="icon-preview">
                  <img :src="formData.icon_image_url" alt="图标预览" />
                  <button type="button" @click="removeIcon" class="remove-icon-btn">移除</button>
              </div>
                <div class="upload-tip">
                  建议尺寸：64x64px 或 128x128px，支持 PNG、SVG 格式，大小不超过 2MB
                </div>
              </div>

              <div class="form-group">
                <label class="checkbox-label">
                  <input 
                    type="checkbox" 
                    v-model="formData.is_hot"
                  />
                  设为热门分类
                </label>
              </div>
              
              <!-- 显示父分类信息（仅在添加二级分类时显示） -->
              <div v-if="formData.parent && !editingCategory" class="form-group">
                <label>父分类</label>
                <div class="parent-category-display">
                  {{ getParentCategoryName(formData.parent) }}
                </div>
              </div>
              <div class="form-actions">
                <button type="button" class="cancel-btn" @click="closeDialog">取消</button>
                <button type="submit" class="submit-btn">{{ editingCategory ? '更新' : '创建' }}</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import AdminSidebar from '@/components/admin/AdminSidebar.vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import adminService from '@/services/adminService';

// 响应式数据（删除未使用的 parentCategories）
const categories = ref([]);
const totalCount = ref(0);
const currentPage = ref(1);
const pageSize = ref(50);
const searchQuery = ref('');
const showAddDialog = ref(false);
const showDialog = ref(false);
const editingCategory = ref(null);
const expandedCategories = ref([]);
const formData = ref({
  name: '',
  description: '',
  icon_image: null,
  icon_image_url: '',
  parent: '',
  is_hot: false
});

// 计算属性
// totalPages 计算属性在当前组件中未使用，已移除以避免编译器警告

// 获取一级分类列表
const parentCategoriesList = computed(() => {
  return categories.value.filter(cat => {
    return cat.parent === null || cat.parent === undefined;
  });
});

// 获取指定一级分类的二级分类
const getSubcategories = (parentId) => {
  return categories.value.filter(cat => {
    return cat.parent !== null && cat.parent !== undefined && cat.parent === parentId;
  });
};

// 切换折叠面板状态
const toggleAccordion = (categoryId) => {
  const index = expandedCategories.value.indexOf(categoryId);
  if (index > -1) {
    expandedCategories.value.splice(index, 1);
  } else {
    expandedCategories.value.push(categoryId);
  }
};

// 添加二级分类
const addSubcategory = (parentId) => {
  const parent = categories.value.find(cat => cat.id === parentId);
  if (parent) {
    resetForm();
    formData.value.parent = parentId;
    showDialog.value = true;
    if (!expandedCategories.value.includes(parentId)) {
      expandedCategories.value.push(parentId);
    }
    ElMessage.info(`添加${parent.name}的二级分类`);
  }
};

// 获取分类列表（删除冗余的 parent_id 过滤逻辑）
const fetchCategories = async () => {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    };
    
    if (searchQuery.value) {
      params.search = searchQuery.value;
    }
    
    const response = await adminService.getCategories(params);
    // 处理不同的数据结构
    if (response.results) {
      categories.value = response.results;
      totalCount.value = response.count || response.results.length;
    } else if (Array.isArray(response)) {
      categories.value = response;
      totalCount.value = response.length;
    } else {
      console.warn('未知的数据结构:', response);
      categories.value = [];
      totalCount.value = 0;
    }
  } catch (error) {
    console.error('获取分类列表错误详情:', error);
    ElMessage.error('获取分类列表失败：' + (error.message || '未知错误'));
  }
};

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1;
  fetchCategories();
};


// 打开添加对话框
const openAddDialog = () => {
  editingCategory.value = null;
  resetForm();
  showDialog.value = true;
};

// 编辑分类
const editCategory = (category) => {
  editingCategory.value = category;
  formData.value = {
    name: category.name,
    description: category.description || '',
    icon_image: null,
    icon_image_url: category.icon_image_url || '',
    parent: category.parent || '',
    is_hot: category.is_hot || false
  };
  showDialog.value = true;
};

// 处理图标上传
const handleIconUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      ElMessage.error('只能上传图片文件！');
      return;
    }
    // 验证文件大小（2MB）
    if (file.size > 2 * 1024 * 1024) {
      ElMessage.error('图片大小不能超过 2MB！');
      return;
    }
    formData.value.icon_image = file;
    // 预览图片
    const reader = new FileReader();
    reader.onload = (e) => {
      formData.value.icon_image_url = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

// 移除图标
const removeIcon = () => {
  formData.value.icon_image = null;
  formData.value.icon_image_url = '';
  // 清空文件输入
  const fileInput = document.getElementById('categoryIcon');
  if (fileInput) {
    fileInput.value = '';
  }
};

// 保存分类（创建或更新）
const saveCategory = async () => {
  try {
    // 验证必填字段
    if (!formData.value.name.trim()) {
      ElMessage.warning('请输入分类名称');
      return;
    }
    
    // 构建FormData用于文件上传
    const formDataToSend = new FormData();
    formDataToSend.append('name', formData.value.name);
    formDataToSend.append('description', formData.value.description || '');
    formDataToSend.append('is_hot', formData.value.is_hot);
    if (formData.value.parent) {
      formDataToSend.append('parent_id', formData.value.parent);
    }
    // 如果有新上传的图片，添加图片文件
    if (formData.value.icon_image) {
      formDataToSend.append('icon_image', formData.value.icon_image);
    }
    
    if (editingCategory.value) {
      await adminService.updateCategory(editingCategory.value.id, formDataToSend);
      ElMessage.success('分类更新成功！');
    } else {
      await adminService.createCategory(formDataToSend);
      const categoryType = formData.value.parent ? '二级分类' : '一级分类';
      ElMessage.success(`${categoryType}创建成功！`);
    }
    
    closeDialog();
    fetchCategories();
  } catch (error) {
    console.error('分类操作失败:', error);
    ElMessage.error('操作失败：' + error.message);
  }
};

// 删除分类
const deleteCategory = async (categoryId) => {
  const category = categories.value.find(cat => cat.id === categoryId);
  const categoryName = category ? category.name : '该分类';
  
  try {
    await ElMessageBox.confirm(
      `确定要永久删除分类"${categoryName}"吗？此操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
        showClose: false
      }
    );
    
    await adminService.deleteCategory(categoryId);
    ElMessage.success(`分类"${categoryName}"删除成功！`);
    fetchCategories();
  } catch (error) {
    if (error === 'cancel' || error.name === 'CanceledError') {
      console.log('用户取消了删除操作');
      return;
    }
    console.error('删除分类失败:', error);
    const errorMessage = error.message || '删除失败，请稍后重试';
    ElMessage.error(`删除失败：${errorMessage}`);
  }
};

// 切换热门状态（删除无效的嵌套subcategories处理）
const toggleHotStatus = async (categoryId, isHot) => {
  try {
    await adminService.toggleCategoryHotStatus(categoryId, isHot);
    ElMessage.success('状态更新成功！');
    // 更新本地数据（仅处理平级的categories数组）
    const category = categories.value.find(c => c.id === categoryId);
    if (category) {
      category.is_hot = isHot;
    }
  } catch (error) {
    console.error('切换热门状态失败:', error);
    ElMessage.error('状态更新失败：' + error.message);
    // 恢复原状态
    const category = categories.value.find(c => c.id === categoryId);
    if (category) {
      category.is_hot = !isHot;
    }
  }
};

// 关闭对话框
const closeDialog = () => {
  showDialog.value = false;
  showAddDialog.value = false;
  resetForm();
};

// 获取父分类名称
const getParentCategoryName = (parentId) => {
  const parent = categories.value.find(cat => cat.id === parentId);
  return parent ? parent.name : '未设置';
};

// 重置表单
const resetForm = () => {
  formData.value = {
    name: '',
    description: '',
    icon_image: null,
    icon_image_url: '',
    parent: '',
    is_hot: false
  };
  editingCategory.value = null;
  // 清空文件输入
  const fileInput = document.getElementById('categoryIcon');
  if (fileInput) {
    fileInput.value = '';
  }
};

// 监听showAddDialog，触发添加对话框
watch(() => showAddDialog.value, (newVal) => {
  if (newVal) {
    openAddDialog();
  }
});

// 组件挂载时初始化数据（删除调用fetchParentCategories的代码）
onMounted(async () => {
  await fetchCategories();
});
</script>
  
<style scoped>
  .admin-dashboard {
    display: flex;
    min-height: 100vh;
    background-color: #f5f7fa;
  }
  
  /* 设置表单输入元素的宽度 */
  #categoryName,
  #categoryDescription,
  #categoryIcon {
    width: 95%;
  }
  
  .icon-preview {
    margin-top: 10px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .icon-preview img {
    width: 64px;
    height: 64px;
    object-fit: contain;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 4px;
  }
  
  .remove-icon-btn {
    padding: 4px 12px;
    background: #ef4444;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
  }
  
  .remove-icon-btn:hover {
    background: #dc2626;
  }
  
  .upload-tip {
    margin-top: 5px;
    font-size: 12px;
    color: #6b7280;
  }
  
  .category-icon-img {
    width: 24px;
    height: 24px;
    object-fit: contain;
    margin-right: 8px;
  }
  
  .category-icon-placeholder {
    width: 24px;
    height: 24px;
    border-radius: 4px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: bold;
    margin-right: 8px;
  }

  .admin-content {
    flex: 1;
    padding: 20px;
    margin-left: 240px;
    min-height: 100vh;
    box-sizing: border-box;
  }

  .admin-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .add-btn {
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

  .add-btn:hover {
    background-color: #2563eb;
  }

  .filter-section {
    margin-bottom: 20px;
  }

  /* 统一搜索样式 */
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

  .category-list {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  /* 折叠面板样式 */
  .accordion {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .accordion-item {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.2s ease;
  }

  .accordion-item:hover {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .accordion-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    background-color: #f9fafb;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .accordion-header:hover {
    background-color: #f3f4f6;
  }

  .accordion-header i {
    margin-right: 12px;
    color: #6b7280;
    transition: transform 0.3s ease;
  }

  .accordion-header i.rotate-180 {
    transform: rotate(180deg);
  }

  .category-info {
    flex: 1;
  }

  .category-title {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
    font-weight: 600;
    font-size: 16px;
    color: #1f2937;
  }

  .category-title i {
    color: #3b82f6;
    font-size: 18px;
    margin-right: 6px;
  }

  .category-badge {
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 500;
  }

  .category-badge.primary {
    background-color: #dbeafe;
    color: #1e40af;
  }

  .category-badge.secondary {
    background-color: #e0f2fe;
    color: #0c4a6e;
  }

  .category-meta {
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 14px;
    color: #6b7280;
  }

  .hot-status {
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    background-color: #fef3c7;
    color: #92400e;
  }

  .description {
    flex: 1;
    max-width: 500px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .icon-color {
    font-size: 12px;
    font-weight: 500;
  }

  .category-actions {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .accordion-content {
    transition: all 0.3s ease;
    padding: 0;
  }

  .subcategories-container {
    padding: 16px;
    background-color: #fafafa;
  }

  .subcategory-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    margin-bottom: 12px;
    background-color: white;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    transition: all 0.2s;
  }

  .subcategory-item:hover {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    border-color: #d1d5db;
  }

  .subcategory-item:last-child {
    margin-bottom: 0;
  }

  .no-subcategories {
    text-align: center;
    padding: 32px 16px;
    color: #6b7280;
  }

  .no-subcategories p {
    margin-bottom: 16px;
  }

  /* 添加二级分类按钮样式 */
  .add-subcategory-section {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #e5e7eb;
    display: flex;
    justify-content: flex-start;
  }

  .add-subcategory-btn {
    background-color: #10b981;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 5px;
    transition: background-color 0.2s;
  }

  .add-subcategory-btn:hover {
    background-color: #059669;
  }

  .no-categories {
    text-align: center;
    padding: 64px 20px;
    color: #6b7280;
  }

  /* 开关样式 */
  .switch {
    position: relative;
    display: inline-block;
    width: 40px;
    height: 20px;
  }

  .switch input {
    opacity: 0;
    width: 0;
    height: 0;
  }

  .slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: .4s;
    border-radius: 20px;
  }

  .slider:before {
    position: absolute;
    content: "";
    height: 16px;
    width: 16px;
    left: 2px;
    bottom: 2px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
  }

  input:checked + .slider {
    background-color: #2196F3;
  }

  input:focus + .slider {
    box-shadow: 0 0 1px #2196F3;
  }

  input:checked + .slider:before {
    transform: translateX(20px);
  }

  /* 按钮样式 */
  .edit-btn {
    background-color: #3b82f6;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 1px;
    font-size: 12px;
    transition: background-color 0.3s;
  }

  .edit-btn:hover {
    background-color: #2563eb;
  }

  .edit-btn i {
    color: white;
    font-size: 11px;
    margin-right: 1px;
    margin-left: 0;
  }

  .delete-btn {
    background-color: #ef4444;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 1px;
    font-size: 12px;
    transition: background-color 0.3s;
  }

  .delete-btn:hover {
    background-color: #dc2626;
  }

  .delete-btn i {
    color: white;
    font-size: 11px;
    margin-right: 1px;
    margin-left: 0;
  }

  /* 模态框样式 */
  .modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .modal-content {
    background-color: white;
    border-radius: 8px;
    width: 90%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
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
    font-size: 18px;
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #6b7280;
  }

  .modal-body {
    padding: 20px;
  }

  .form-group {
    margin-bottom: 20px;
  }

  .form-group label {
    display: block;
    margin-bottom: 6px;
    font-weight: 500;
  }

  .form-group input,
  .form-group textarea {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    font-size: 14px;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    cursor: pointer;
  }

  .checkbox-label input {
    width: auto;
    margin-right: 8px;
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 30px;
  }
  
  /* 父分类显示区域样式 */
  .parent-category-display {
    padding: 8px 12px;
    background-color: #f5f7fa;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    color: #606266;
    font-size: 14px;
    cursor: default;
    margin-top: 5px;
  }

  .submit-btn {
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

  .submit-btn:hover {
    background-color: #2563eb;
  }

  .cancel-btn {
    background-color: #6b7280;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: background-color 0.3s;
  }

  .cancel-btn:hover {
    background-color: #4b5563;
  }
</style>