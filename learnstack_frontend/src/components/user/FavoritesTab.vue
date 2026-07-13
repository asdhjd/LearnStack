<template>
  <div class="tab-panel">
    <div class="favorites-content">
      <!-- 标题和批量删除按钮容器 -->
      <div class="page-header">
        <div class="page-header-left">
          <h2 class="section-title">我的收藏</h2>
          <p class="section-subtitle">集中管理你关注的资源，随时回顾与整理</p>
        </div>
        <div class="header-actions">
          <button @click="showCreateCategoryModal = true" class="create-category-btn">
            <i class="fas fa-plus"></i> 创建分类
          </button>
          <button @click="deleteSelected" class="batch-delete-btn" :disabled="selectedIds.length === 0">
            <i class="fas fa-trash-alt"></i> 批量删除（{{ selectedIds.length }}）
          </button>
        </div>
      </div>

      <div class="favorites-summary">
        <div class="summary-card">
          <span class="summary-label">收藏数量</span>
          <span class="summary-value">{{ favorites.length }}</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">分类数量</span>
          <span class="summary-value">{{ categories.length }}</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">已选择</span>
          <span class="summary-value">{{ selectedIds.length }}</span>
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
          <div class="card-media">
            <img :src="getCoverImage(item)" alt="资源封面" @error="handleCoverError($event)">
            <div class="media-badges">
              <span class="media-badge type">{{ getResourceTypeLabel(item) }}</span>
            </div>
            <label class="select-pill">
              <input 
                type="checkbox" 
                v-model="selectedIds" 
                :value="item.id"
              />
              <span>选中</span>
            </label>
          </div>
          <div class="card-content">
            <div class="card-title-row">
              <h3 class="card-title">{{ getFavoriteTitle(item) }}</h3>
              <span class="card-date">{{ formatFavoriteDate(item.created_at) }}</span>
            </div>
            <p v-if="getResourceDescription(item)" class="card-description">
              {{ getResourceDescription(item) }}
            </p>
            <div class="card-meta-row">
              <span v-if="getReadingTime(item)" class="meta-chip">
                <i class="fas fa-clock"></i>{{ getReadingTime(item) }}
              </span>
              <span v-if="getFavoriteLevel(item)" class="meta-chip">
                <i class="fas fa-signal"></i>{{ getFavoriteLevel(item) }}
              </span>
            </div>
            <div class="card-footer-actions">
              <button
                class="action-btn primary"
                @click="handleViewFavorite(item)"
                :disabled="!canViewFavorite(item)"
              >
                <i class="fas" :class="canViewFavorite(item) ? 'fa-book-open' : 'fa-ban'"></i>
                <span>{{ getViewButtonLabel(item) }}</span>
              </button>
              <button @click="confirmDeleteFavorite(item)" class="action-btn danger">
                <i class="fas fa-trash"></i>
                <span>删除</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 收藏相关弹窗 -->
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
    <div v-if="showDeleteFavoriteConfirm" class="modal-overlay" @click.self="showDeleteFavoriteConfirm = false">
      <div class="modal-content">
        <h3>确认删除</h3>
        <p>确定要删除收藏「{{ getFavoriteTitle(favoriteToDelete) }}」吗？此操作不可恢复。</p>
        <div class="modal-actions">
          <button @click="showDeleteFavoriteConfirm = false" class="cancel-btn">取消</button>
          <button @click="deleteFavorite" class="danger-btn">删除</button>
        </div>
      </div>
    </div>

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
import { ref, computed, onMounted, getCurrentInstance } from 'vue';
import { useRouter } from 'vue-router';
import { 
  getFavorites, 
  deleteFavorites, 
  getFavoriteCategories, 
  createFavoriteCategory, 
  updateCategoryName,
  deleteFavoriteCategory,
  updateFavoriteCategoryAssignment
} from '@/services/favoriteService';

const { appContext } = getCurrentInstance();
const mediaUrl = appContext?.config?.globalProperties?.mediaUrl || '';
const defaultCover = '/default-cover.png';

const router = useRouter();
const favorites = ref([]);
const categories = ref([]);
const selectedIds = ref([]);
const selectedCategoryId = ref(null);
const defaultCategoryId = ref(null);
const showCreateCategoryModal = ref(false);
const showEditCategoryModal = ref(false);
const showMoveToModal = ref(false);
const showDeleteCategoryConfirm = ref(false);
const showDeleteFavoriteConfirm = ref(false);
const newCategoryName = ref('');
const editingCategory = ref({ id: null, name: '' });
const selectedFavoriteId = ref(null);
const selectedTargetCategoryId = ref(null);
const categoryToDelete = ref(null);
const favoriteToDelete = ref(null);

const resourceTypeLabelMap = {
  book: '书籍',
  course: '课程',
  article: '文章',
  project: '项目',
  tool: '工具',
  document: '文档',
};

const filteredFavorites = computed(() => {
  if (!selectedCategoryId.value) {
    return favorites.value;
  }
  return favorites.value.filter(item => item.category && item.category.id === selectedCategoryId.value);
});

// 防止重复加载的标记
let isLoading = false;
let isMounted = false;

onMounted(async () => {
  if (isMounted) return; // 防止重复挂载
  isMounted = true;
  await loadData();
});

const loadData = async () => {
  if (isLoading) return; // 防止重复请求
  isLoading = true;
  try {
    const categoriesData = await getFavoriteCategories();
    categories.value = categoriesData;
    const defaultCategory = categoriesData.find(cat => cat.name === '默认收藏夹');
    if (defaultCategory) {
      defaultCategoryId.value = defaultCategory.id;
      selectedCategoryId.value = defaultCategory.id;
      categories.value.sort((a, b) => {
        if (a.id === defaultCategoryId.value) return -1;
        if (b.id === defaultCategoryId.value) return 1;
        return 0;
      });
    }
    await loadFavorites();
  } catch (error) {
    console.error('加载数据失败:', error);
  } finally {
    isLoading = false;
  }
};

// 防止重复加载收藏列表的标记
let isLoadingFavorites = false;

const loadFavorites = async () => {
  if (isLoadingFavorites) return; // 防止重复请求
  isLoadingFavorites = true;
  try {
    favorites.value = await getFavorites();
    selectedIds.value = [];
  } catch (error) {
    console.error('加载收藏列表失败:', error);
  } finally {
    isLoadingFavorites = false;
  }
};

const switchCategory = (categoryId) => {
  selectedCategoryId.value = categoryId;
  selectedIds.value = [];
};

const createCategory = async () => {
  if (!newCategoryName.value.trim()) return;
  try {
    const newCategory = await createFavoriteCategory(newCategoryName.value.trim());
    categories.value.push(newCategory);
    newCategoryName.value = '';
    showCreateCategoryModal.value = false;
    if (categories.value.length === 1) {
      selectedCategoryId.value = newCategory.id;
    }
  } catch (error) {
    alert('创建分类失败: ' + (error.response?.data?.detail || '未知错误'));
  }
};

const editCategory = (category) => {
  editingCategory.value = { ...category };
  showEditCategoryModal.value = true;
};

const updateCategory = async () => {
  if (!editingCategory.value.name.trim()) return;
  try {
    await updateCategoryName(editingCategory.value.id, editingCategory.value.name.trim());
    const categoryIndex = categories.value.findIndex(cat => cat.id === editingCategory.value.id);
    if (categoryIndex !== -1) {
      categories.value[categoryIndex].name = editingCategory.value.name;
    }
    showEditCategoryModal.value = false;
  } catch (error) {
    alert('更新分类失败: ' + (error.response?.data?.detail || '未知错误'));
  }
};

const confirmDeleteCategory = (category) => {
  if (category.id === defaultCategoryId.value) {
    alert('默认收藏夹不能删除');
    return;
  }
  categoryToDelete.value = category;
  showDeleteCategoryConfirm.value = true;
};

const deleteCategory = async () => {
  if (!categoryToDelete.value) return;
  const confirmed = window.confirm(`确定要删除分类「${categoryToDelete.value.name}」吗？该分类下的收藏将移至默认收藏夹。`);
  if (!confirmed) return;

  try {
    await deleteFavoriteCategory(categoryToDelete.value.id);
    categories.value = categories.value.filter(cat => cat.id !== categoryToDelete.value.id);
    if (selectedCategoryId.value === categoryToDelete.value.id) {
      selectedCategoryId.value = defaultCategoryId.value;
    }
    await loadFavorites();
    showDeleteCategoryConfirm.value = false;
    categoryToDelete.value = null;
  } catch (error) {
    alert('删除分类失败: ' + (error.response?.data?.detail || '未知错误'));
  }
};

const moveToCategory = async () => {
  if (!selectedFavoriteId.value || selectedTargetCategoryId.value === undefined) return;
  try {
    await updateFavoriteCategoryAssignment(selectedFavoriteId.value, selectedTargetCategoryId.value);
    const favoriteIndex = favorites.value.findIndex(fav => fav.id === selectedFavoriteId.value);
    if (favoriteIndex !== -1) {
      const targetCategory = categories.value.find(cat => cat.id === selectedTargetCategoryId.value);
      favorites.value[favoriteIndex].category = targetCategory;
    }
    await loadCategoriesWithCount();
    showMoveToModal.value = false;
    selectedFavoriteId.value = null;
    selectedTargetCategoryId.value = null;
  } catch (error) {
    alert('移动收藏失败: ' + (error.response?.data?.detail || '未知错误'));
  }
};

const loadCategoriesWithCount = async () => {
  try {
    categories.value = await getFavoriteCategories();
  } catch (error) {
    console.error('加载分类失败:', error);
  }
};

const deleteSelected = async () => {
  if (selectedIds.value.length === 0) {
    alert('请选择需要删除的收藏项');
    return;
  }
  try {
    await deleteFavorites(selectedIds.value);
    favorites.value = favorites.value.filter(item => !selectedIds.value.includes(item.id));
    selectedIds.value = [];
    await loadCategoriesWithCount();
  } catch (error) {
    console.error('批量删除收藏失败:', error);
    alert('批量删除失败');
  }
};

const getResourceTypeLabel = (favorite) => {
  const key = favorite?.content_object?.resource_type;
  return resourceTypeLabelMap[key] || '资源';
};

const formatFavoriteDate = (dateString) => {
  if (!dateString) return '未知时间';
  return new Date(dateString).toLocaleDateString('zh-CN');
};

const getResourceDescription = (favorite) => {
  return favorite?.content_object?.summary || favorite?.content_object?.description || '';
};

const getCoverImage = (favorite) => {
  const cover =
    favorite?.content_object?.hero_cover ||
    favorite?.content_object?.cover ||
    favorite?.content_object?.cover_url ||
    favorite?.content_object?.thumbnail ||
    '';

  if (!cover) return defaultCover;
  if (cover.startsWith('data:image') || cover.startsWith('http')) return cover;
  if (mediaUrl && cover.startsWith('/')) {
    return `${mediaUrl}${cover.replace(/^\//, '')}`;
  }
  if (mediaUrl && !cover.startsWith('http')) {
    return `${mediaUrl}${cover}`;
  }
  return cover || defaultCover;
};

const handleCoverError = (event) => {
  // 防止无限循环：如果已经是默认封面，就不再尝试加载
  if (event.target.src && event.target.src.includes('default-cover.png')) {
    // 如果默认封面也加载失败，设置为空或隐藏图片
    event.target.style.display = 'none';
    return;
  }
  // 尝试加载默认封面
  event.target.src = defaultCover;
  // 如果默认封面加载失败，设置一个标记防止再次触发
  event.target.onerror = () => {
    event.target.style.display = 'none';
  };
};

const getFavoriteTitle = (favorite) => {
  if (!favorite) return '该收藏';
  return favorite.content_object?.title || '未知资源';
};

const getReadingTime = (favorite) => {
  return favorite?.content_object?.reading_time || '';
};

const getFavoriteLevel = (favorite) => {
  return favorite?.content_object?.level || '';
};

const confirmDeleteFavorite = (favorite) => {
  favoriteToDelete.value = favorite;
  showDeleteFavoriteConfirm.value = true;
};

const canViewFavorite = (favorite) => {
  return Boolean(favorite?.content_object?.id || favorite?.content_object?.url);
};

const getViewButtonLabel = (favorite) => {
  if (favorite?.content_object?.id) return '查看详情';
  if (favorite?.content_object?.url) return '访问链接';
  return '暂无链接';
};

const handleViewFavorite = (favorite) => {
  if (favorite?.content_object?.id) {
    const routeData = router.resolve({ name: 'ResourceDetail', params: { id: favorite.content_object.id } });
    window.open(routeData.href, '_blank', 'noopener');
    return;
  }
  if (favorite?.content_object?.url) {
    window.open(favorite.content_object.url, '_blank', 'noopener');
  }
};

const deleteFavorite = async () => {
  if (!favoriteToDelete.value) return;
  const id = favoriteToDelete.value.id;

  try {
    await deleteFavorites([id]);
    favorites.value = favorites.value.filter(item => item.id !== id);
    selectedIds.value = selectedIds.value.filter(selectedId => selectedId !== id);
    await loadCategoriesWithCount();
  } catch (error) {
    console.error('删除收藏失败:', error);
    alert('删除失败');
  } finally {
    favoriteToDelete.value = null;
    showDeleteFavoriteConfirm.value = false;
  }
};
</script>

<style scoped>
.tab-panel {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.favorites-content {
  background: #ffffff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.section-title {
  font-size: 1.5rem;
  color: #111827;
  margin: 0;
  font-weight: 600;
}

.section-subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 0.95rem;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.batch-delete-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  box-shadow: none;
}

.favorites-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 28px;
}

.summary-card {
  background: #f9fafb;
  border-radius: 12px;
  padding: 16px 20px;
  border: 1px solid #e5e7eb;
}

.summary-label {
  display: block;
  color: #6b7280;
  font-size: 0.9rem;
  margin-bottom: 6px;
}

.summary-value {
  font-size: 1.3rem;
  color: #111827;
  font-weight: 600;
}

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

.empty-message {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
  font-size: 1.1rem;
  background: #f9fafb;
  border-radius: 12px;
  border: 2px dashed #e5e7eb;
}

.favorites-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  align-items: stretch;
}

.favorite-card {
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.12);
  border: 1px solid rgba(226, 232, 240, 0.9);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  width: 100%;
}

.favorite-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 28px rgba(15, 23, 42, 0.15);
}

.card-media {
  position: relative;
  height: 150px;
  overflow: hidden;
}

.card-media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.favorite-card:hover .card-media img {
  transform: scale(1.04);
}

.media-badges {
  position: absolute;
  top: 16px;
  left: 16px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.media-badge {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
  color: #fff;
}

.media-badge.type {
  background: rgba(37, 99, 235, 0.9);
}

.select-pill {
  position: absolute;
  top: 16px;
  right: 16px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 0.78rem;
  color: #111827;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.select-pill input {
  width: 14px;
  height: 14px;
  cursor: pointer;
}

.card-content {
  padding: 16px 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 190px;
}

.card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.card-title {
  margin: 0;
  font-size: 1.08rem;
  color: #0f172a;
  font-weight: 600;
}

.card-date {
  font-size: 0.78rem;
  color: #94a3b8;
  white-space: nowrap;
}

.card-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
  font-size: 0.78rem;
}

.meta-chip i {
  color: #94a3b8;
  font-size: 0.75rem;
}

.card-footer-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid #eef2f7;
  width: 100%;
}

.card-footer-actions .action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 6px;
  border: none;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
  height: 34px;
  min-width: 88px;
  flex: 1 1 0;
  justify-content: center;
  font-weight: 500;
}

.card-footer-actions .action-btn.primary {
  background: linear-gradient(135deg, #4f46e5, #2563eb);
  color: #fff;
  box-shadow: 0 6px 14px rgba(37, 99, 235, 0.25);
}

.card-footer-actions .action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

.card-footer-actions .action-btn.primary:hover {
  background: linear-gradient(135deg, #4338ca, #1d4ed8);
}

.card-footer-actions .action-btn.danger {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.card-footer-actions .action-btn.danger:hover {
  background: #fecaca;
}

.card-description {
  margin: 0;
  color: #4b5563;
  line-height: 1.45;
  font-size: 0.9rem;
}

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

.category-input,
.category-select {
  width: 90%;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  margin-bottom: 24px;
  transition: border-color 0.3s;
  background: white;
}

.category-input:focus,
.category-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

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
  background: #ef4444;
  color: white;
}

.danger-btn:hover {
  background: #dc2626;
}

@media (max-width: 768px) {
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
    justify-content: center;
  }
  
  .card-media {
    height: 150px;
  }
  
  .favorite-card {
    width: 100%;
  }
  
  .card-footer-actions {
    width: 100%;
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .card-footer-actions .action-btn {
    flex: 1 1 140px;
    justify-content: center;
  }
  
  .modal-content {
    min-width: auto;
    width: 90%;
    padding: 24px;
  }

  .favorites-summary {
    grid-template-columns: 1fr;
  }
}
</style>

