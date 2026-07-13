<template>
  <div class="favorites-container">
    <!-- 标题和批量删除按钮容器 -->
    <div class="page-header">
      <h2 class="page-title">我的收藏</h2>
      <div class="header-actions">
        <!-- 创建分类按钮 -->
        <button @click="showCreateCategoryModal = true" class="create-category-btn">
          <i class="fas fa-plus"></i> 创建分类
        </button>
        <!-- 批量删除按钮 -->
        <button @click="deleteSelected" class="batch-delete-btn">
          <i class="fas fa-trash-alt"></i> 批量删除选中项（{{ selectedIds.length }}）
        </button>
      </div>
    </div>

    <!-- 分类选择区域 -->
    <div class="categories-section">
      <div class="categories-tabs">
        <div 
          v-for="category in categories" 
          :key="category.id"
          class="category-tab"
          :class="{ active: selectedCategoryId === category.id }"
          @click="switchCategory(category.id)"
        >
          <span>{{ category.name }}</span>
          <span class="count">({{ category.favorite_count }})</span>
          <div class="category-actions" v-if="category.id !== defaultCategoryId">
            <button @click.stop="editCategory(category)" class="edit-btn">
              <i class="fas fa-edit"></i>
            </button>
            <button @click.stop="confirmDeleteCategory(category)" class="delete-btn">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="favorites-list">
      <div v-if="filteredFavorites.length === 0" class="empty-message">
        {{ selectedCategoryId ? '该分类下暂无收藏内容' : '暂无收藏内容' }}
      </div>
      <div v-else v-for="item in filteredFavorites" :key="item.id" class="favorite-card">
        <div class="card-content">
          <!-- 多选框 -->
          <input 
            type="checkbox" 
            v-model="selectedIds" 
            :value="item.id" 
            class="select-checkbox"
          >
          
          <!-- 资源标题 -->
          <span class="title">{{ item.content_object && item.content_object.title || '未知资源' }}</span>
          
          <!-- 按钮组容器 -->
          <div class="button-group">
            <!-- 查看资源按钮 -->
            <router-link
              v-if="item.content_object && item.content_object.id"
              :to="{ name: 'ResourceDetail', params: { id: item.content_object.id } }"
              class="view-btn"
            >
              <i class="fas fa-book-open"></i> 查看资源
            </router-link>
            <a
              v-else
              :href="item.content_object && item.content_object.url || '#'"
              target="_blank"
              rel="noopener"
              class="view-btn"
            >
              <i class="fas fa-external-link-alt"></i> 查看资源
            </a>
            
            <!-- 删除按钮 -->
            <button @click="deleteFavorite(item.id)" class="delete-btn">
              <i class="fas fa-trash"></i> 删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建分类弹窗 -->
    <div v-if="showCreateCategoryModal" class="modal-overlay" @click.self="showCreateCategoryModal = false">
      <div class="modal-content">
        <h3>创建收藏夹分类</h3>
        <input 
          v-model="newCategoryName" 
          type="text" 
          placeholder="请输入分类名称"
          @keyup.enter="createCategory"
          class="category-input"
        >
        <div class="modal-actions">
          <button @click="showCreateCategoryModal = false" class="cancel-btn">取消</button>
          <button @click="createCategory" class="confirm-btn" :disabled="!newCategoryName.trim()">创建</button>
        </div>
      </div>
    </div>

    <!-- 编辑分类弹窗 -->
    <div v-if="showEditCategoryModal" class="modal-overlay" @click.self="showEditCategoryModal = false">
      <div class="modal-content">
        <h3>编辑收藏夹分类</h3>
        <input 
          v-model="editingCategory.name" 
          type="text" 
          placeholder="请输入分类名称"
          @keyup.enter="updateCategory"
          class="category-input"
        >
        <div class="modal-actions">
          <button @click="showEditCategoryModal = false" class="cancel-btn">取消</button>
          <button @click="updateCategory" class="confirm-btn" :disabled="!editingCategory.name.trim()">保存</button>
        </div>
      </div>
    </div>

    <!-- 移动到分类弹窗 -->
    <div v-if="showMoveToModal" class="modal-overlay" @click.self="showMoveToModal = false">
      <div class="modal-content">
        <h3>移动到分类</h3>
        <select v-model="selectedTargetCategoryId" class="category-select">
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
        <div class="modal-actions">
          <button @click="showMoveToModal = false" class="cancel-btn">取消</button>
          <button @click="moveToCategory" class="confirm-btn">确定</button>
        </div>
      </div>
    </div>

    <!-- 删除分类确认弹窗 -->
    <div v-if="showDeleteCategoryConfirm" class="modal-overlay" @click.self="showDeleteCategoryConfirm = false">
      <div class="modal-content">
        <h3>确认删除</h3>
        <p>确定要删除分类 "{{ (categoryToDelete && categoryToDelete.name) || '未知分类' }}" 吗？该分类下的收藏将会移至默认收藏夹。</p>
        <div class="modal-actions">
          <button @click="showDeleteCategoryConfirm = false" class="cancel-btn">取消</button>
          <button @click="deleteCategory" class="danger-btn">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue';
import { 
  getFavorites, 
  deleteFavorites, 
  getFavoriteCategories, 
  createFavoriteCategory, 
  updateCategoryName,
  deleteFavoriteCategory,
  updateFavoriteCategoryAssignment
} from '@/services/favoriteService';

defineOptions({
  name: 'UserFavorites'
});

const favorites = ref([]);
const categories = ref([]);
const selectedIds = ref([]);  // 存储选中的收藏ID
const selectedCategoryId = ref(null);  // 当前选中的分类ID
const defaultCategoryId = ref(null);  // 默认收藏夹ID

// 弹窗状态
const showCreateCategoryModal = ref(false);
const showEditCategoryModal = ref(false);
const showMoveToModal = ref(false);
const showDeleteCategoryConfirm = ref(false);

// 表单数据
const newCategoryName = ref('');
const editingCategory = ref({ id: null, name: '' });
const selectedFavoriteId = ref(null);
const selectedTargetCategoryId = ref(null);
const categoryToDelete = ref(null);

// 计算属性：根据选中分类过滤收藏
const filteredFavorites = computed(() => {
  if (!selectedCategoryId.value) {
    return favorites.value;
  }
  return favorites.value.filter(item => item.category && item.category.id === selectedCategoryId.value);
});

// 初始化加载数据
onMounted(async () => {
  await loadData();
});

// 加载收藏和分类数据
const loadData = async () => {
  try {
    // 加载分类
    const categoriesData = await getFavoriteCategories();
    categories.value = categoriesData;
    
    // 找到默认收藏夹
    const defaultCategory = categoriesData.find(cat => cat.name === '默认收藏夹');
    if (defaultCategory) {
      defaultCategoryId.value = defaultCategory.id;
      selectedCategoryId.value = defaultCategory.id; // 默认选中默认收藏夹
      
      // 对分类进行排序，确保默认收藏夹在首位
      categories.value.sort((a, b) => {
        if (a.id === defaultCategoryId.value) return -1;
        if (b.id === defaultCategoryId.value) return 1;
        return 0;
      });
    }
    
    // 加载收藏
    await loadFavorites();
  } catch (error) {
    console.error('加载数据失败:', error);
  }
};

// 加载收藏列表
const loadFavorites = async () => {
  try {
    favorites.value = await getFavorites();
    selectedIds.value = []; // 清空选中状态
  } catch (error) {
    console.error('加载收藏列表失败:', error);
  }
};

// 切换分类
const switchCategory = (categoryId) => {
  selectedCategoryId.value = categoryId;
  selectedIds.value = []; // 切换分类时清空选中状态
};

// 创建分类
const createCategory = async () => {
  if (!newCategoryName.value.trim()) return;
  
  try {
    const newCategory = await createFavoriteCategory(newCategoryName.value.trim());
    categories.value.push(newCategory);
    newCategoryName.value = '';
    showCreateCategoryModal.value = false;
    
    // 如果是第一个分类，选中它
    if (categories.value.length === 1) {
      selectedCategoryId.value = newCategory.id;
    }
  } catch (error) {
    alert('创建分类失败: ' + (error.response?.data?.detail || '未知错误'));
  }
};

// 编辑分类
const editCategory = (category) => {
  editingCategory.value = { ...category };
  showEditCategoryModal.value = true;
};

// 更新分类
const updateCategory = async () => {
  if (!editingCategory.value.name.trim()) return;
  
  try {
    await updateCategoryName(editingCategory.value.id, editingCategory.value.name.trim());
    
    // 更新本地分类列表
    const categoryIndex = categories.value.findIndex(cat => cat.id === editingCategory.value.id);
    if (categoryIndex !== -1) {
      categories.value[categoryIndex].name = editingCategory.value.name;
    }
    
    showEditCategoryModal.value = false;
  } catch (error) {
    alert('更新分类失败: ' + (error.response?.data?.detail || '未知错误'));
  }
};

// 确认删除分类
const confirmDeleteCategory = (category) => {
  if (category.id === defaultCategoryId.value) {
    alert('默认收藏夹不能删除');
    return;
  }
  categoryToDelete.value = category;
  showDeleteCategoryConfirm.value = true;
};

// 删除分类
const deleteCategory = async () => {
  if (!categoryToDelete.value) return;
  
  try {
    await deleteFavoriteCategory(categoryToDelete.value.id);
    
    // 从本地分类列表中删除
    categories.value = categories.value.filter(cat => cat.id !== categoryToDelete.value.id);
    
    // 如果当前选中的是被删除的分类，切换到默认收藏夹
    if (selectedCategoryId.value === categoryToDelete.value.id) {
      selectedCategoryId.value = defaultCategoryId.value;
    }
    
    // 重新加载收藏列表
    await loadFavorites();
    
    showDeleteCategoryConfirm.value = false;
    categoryToDelete.value = null;
  } catch (error) {
    alert('删除分类失败: ' + (error.response?.data?.detail || '未知错误'));
  }
};

// 移动收藏到指定分类
const moveToCategory = async () => {
  if (!selectedFavoriteId.value || selectedTargetCategoryId.value === undefined) return;
  
  try {
    await updateFavoriteCategoryAssignment(selectedFavoriteId.value, selectedTargetCategoryId.value);
    
    // 更新本地收藏数据
    const favoriteIndex = favorites.value.findIndex(fav => fav.id === selectedFavoriteId.value);
    if (favoriteIndex !== -1) {
      const targetCategory = categories.value.find(cat => cat.id === selectedTargetCategoryId.value);
      favorites.value[favoriteIndex].category = targetCategory;
    }
    
    // 更新分类计数
    await loadCategoriesWithCount();
    
    showMoveToModal.value = false;
    selectedFavoriteId.value = null;
    selectedTargetCategoryId.value = null;
  } catch (error) {
    alert('移动收藏失败: ' + (error.response?.data?.detail || '未知错误'));
  }
};

// 重新加载分类（包含计数）
const loadCategoriesWithCount = async () => {
  try {
    categories.value = await getFavoriteCategories();
  } catch (error) {
    console.error('加载分类失败:', error);
  }
};

// 单个删除
const deleteFavorite = async (id) => {
  try {
    await deleteFavorites([id]);
    favorites.value = favorites.value.filter(item => item.id !== id);
    selectedIds.value = selectedIds.value.filter(selectedId => selectedId !== id);
    
    // 更新分类计数
    await loadCategoriesWithCount();
  } catch (error) {
    console.error('删除收藏失败:', error);
    alert('删除失败');
  }
};

// 批量删除
const deleteSelected = async () => {
  if (selectedIds.value.length === 0) {
    alert('请选择需要删除的收藏项');
    return;
  }
  
  try {
    await deleteFavorites(selectedIds.value);
    favorites.value = favorites.value.filter(item => !selectedIds.value.includes(item.id));
    selectedIds.value = [];
    
    // 更新分类计数
    await loadCategoriesWithCount();
  } catch (error) {
    console.error('批量删除收藏失败:', error);
    alert('批量删除失败');
  }
};
</script>
<style scoped>
/* 新增多选框样式 */
.select-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  margin-right: 12px;
  flex-shrink: 0;
}

.favorites-container {
  padding: 40px 8%;
  max-width: 1440px;
  margin: 0 auto;
}

.page-title {
  font-size: 2.2rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 32px;
}

/* 标题和操作按钮容器 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 创建分类按钮 */
.create-category-btn {
  padding: 10px 20px;
  background: #22c55e;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.create-category-btn:hover {
  background: #16a34a;
}

/* 批量删除按钮 */
.batch-delete-btn {
  padding: 10px 20px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.batch-delete-btn:hover {
  background: #1d4ed8;
}

/* 分类区域样式 */
.categories-section {
  margin-bottom: 32px;
}

.categories-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.category-tab {
  padding: 10px 20px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  user-select: none;
}

.category-tab:hover {
  border-color: #3b82f6;
  transform: translateY(-1px);
}

.category-tab.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.category-tab .count {
  font-size: 0.85rem;
  opacity: 0.8;
}

/* 分类操作按钮 */
.category-actions {
  display: flex;
  gap: 4px;
  margin-left: 8px;
}

.category-actions .edit-btn,
.category-actions .delete-btn {
  background: transparent;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.category-actions .edit-btn:hover {
  background: #eee;
}

.category-actions .delete-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

/* 收藏列表 */
.favorites-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

/* 空状态消息 */
.empty-message {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
  font-size: 1.1rem;
  background: #f9fafb;
  border-radius: 12px;
  border: 2px dashed #e5e7eb;
}

.favorite-card {
  background: white;
  border-radius: 12px;
  padding: 24px 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
  position: relative;
}

.favorite-card:hover {
  transform: translateY(-3px);
  background-color: 0 6px 16px rgba(0, 0, 0, 0.39);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.28);
}

.card-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: nowrap;
}

.title {
  flex: 1;
  color: #111827;
  font-size: 1.1rem;
  line-height: 1.5;
  min-width: 150px;
  max-width: calc(100% - 250px);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}


/* 按钮组容器样式 */
.button-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 100px;
  flex-shrink: 0;
}

/* 查看资源按钮样式 */
.view-btn {
  background: #22c55e;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  gap: 4px;
  text-decoration: none;
  font-size: 0.9rem;
  padding: 6px 12px;
  width: 100px;
  height: 32px;
  justify-content: center;
  flex-shrink: 0;
  box-sizing: border-box;
}

.view-btn:hover {
  background: #16a34a;
}

/* 删除按钮样式 */
.delete-btn {
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  padding: 6px 12px;
  height: 32px;
  justify-content: center;
  flex-shrink: 0;
  box-sizing: border-box;
}

.delete-btn:hover {
  background: #dc2626;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 32px;
  min-width: 400px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #111827;
  font-size: 1.25rem;
  font-weight: 600;
}

/* 输入框样式 */
.category-input {
  width: 94%;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  margin-bottom: 24px;
  transition: border-color 0.3s;
}

.category-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.category-input::placeholder {
  color: #9ca3af;
}

/* 选择框样式 */
.category-select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  margin-bottom: 24px;
  background: white;
  transition: border-color 0.3s;
}

.category-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 模态框操作按钮 */
.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-btn,
.confirm-btn,
.danger-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-btn {
  background: #f3f4f6;
  color: #374151;
}

.cancel-btn:hover {
  background: #e5e7eb;
}

.confirm-btn {
  background: #3b82f6;
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  background: #2563eb;
}

.confirm-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.danger-btn {
  background: #f3f4f6;
  color: #374151;
}

.danger-btn:hover {
  background: #e5e7eb;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .favorites-container {
    padding: 20px 4%;
  }
  
  .page-title {
    font-size: 1.8rem;
  }
  
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 12px;
  }
  
  .create-category-btn,
  .batch-delete-btn {
    width: 100%;
    justify-content: center;
  }
  
  .categories-tabs {
    flex-direction: column;
  }
  
  .category-tab {
    width: 100%;
  }
  
  .favorites-list {
    grid-template-columns: 1fr;
  }
  
  .card-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .title {
    text-align: center;
    margin-bottom: 12px;
  }
  
  .category-label {
    align-self: center;
  }
  
  .button-group {
    flex-direction: row;
    justify-content: center;
    gap: 12px;
  }
  
  .modal-content {
    min-width: auto;
    width: 90%;
    padding: 24px;
  }
}
</style>