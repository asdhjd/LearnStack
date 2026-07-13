import axios from 'axios';
import { API_BASE_URL } from '@/config/api';
const API_URL = `${API_BASE_URL}/favorites/`;

// 获取收藏列表（支持按分类筛选）
export const getFavorites = async (categoryId = null) => {
  try {
    const params = categoryId ? { category: categoryId } : {};
    const res = await axios.get(API_URL, {
      params,
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    });
    return res.data;
  } catch (error) {
    console.log('收藏列表请求失败:', error.response);  // 打印完整响应（含后端错误信息）
    throw error;
  }
};

// 添加收藏（支持指定分类）
export const addFavorite = async (resourceType, resourceId, categoryId = null) => {
  await axios.post(API_URL, { 
    resource_type: resourceType, 
    resource_id: resourceId,
    category_id: categoryId
  }, {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
  });
};

// 批量删除收藏
export const deleteFavorites = async (ids) => {
  await axios.delete(`${API_URL}delete/`, {
    data: { ids },
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
  });
};

// 获取收藏夹分类列表
export const getFavoriteCategories = async () => {
  try {
    const res = await axios.get(`${API_URL}categories/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    });
    return res.data;
  } catch (error) {
    console.log('收藏夹分类列表请求失败:', error.response);
    throw error;
  }
};

// 创建收藏夹分类
export const createFavoriteCategory = async (categoryName) => {
  try {
    const res = await axios.post(`${API_URL}categories/`, {
      name: categoryName
    }, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    });
    return res.data;
  } catch (error) {
    console.log('创建收藏夹分类失败:', error.response);
    throw error;
  }
};

// 更新收藏夹分类名称
export const updateCategoryName = async (categoryId, newName) => {
  try {
    const res = await axios.patch(`${API_URL}categories/${categoryId}/`, {
      name: newName
    }, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    });
    return res.data;
  } catch (error) {
    console.log('更新收藏夹分类失败:', error.response);
    throw error;
  }
};

// 删除收藏夹分类
export const deleteFavoriteCategory = async (categoryId) => {
  try {
    await axios.delete(`${API_URL}categories/${categoryId}/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    });
  } catch (error) {
    console.log('删除收藏夹分类失败:', error.response);
    throw error;
  }
};

// 注意：修复函数名重复的问题
export const updateFavoriteCategoryAssignment = async (favoriteId, categoryId) => {
  await axios.patch(`${API_URL}${favoriteId}/update/`, {
    category_id: categoryId
  }, {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
  });
}